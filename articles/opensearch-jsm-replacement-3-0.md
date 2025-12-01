---
title: "[翻訳] OpenSearch 3.0 における JSM の代替手段"
emoji: "🔐"
type: "tech"
topics: ["opensearch", "java", "security"]
publication_name: "opensearch"
published: true
published_at: 2025-06-03
---

:::message
本記事は [OpenSearch Project Blog](https://opensearch.org/blog/) に投稿された以下の記事を日本語に翻訳したものです。
:::

https://opensearch.org/blog/finding-a-replacement-for-jsm-in-opensearch-3-0/

OpenSearch 3.0.0 では、パフォーマンス、データ管理、ベクトルデータベース機能などにおいて大幅な進歩をもたらす多くの革新的な機能が導入されました。[リリースアナウンス](https://opensearch.org/blog/unveiling-opensearch-3-0/)では、Java Security Manager (JSM) の廃止予定に伴い、OpenSearch が JSM を置き換えたことをお伝えしました。本記事では、この移行を可能にした取り組みについて詳しく説明します。

3.0 で JSM を削除する決定は慎重に検討され、主に 2 つの要因によって推進されました。

1. **Java プラットフォームからの JSM の削除予定**: JSM は JDK 17 以降非推奨となっており ([JEP411](https://openjdk.org/jeps/411))、JDK 24 で完全に削除される予定です ([JEP 486](https://openjdk.org/jeps/486))。Java Enhancement Proposal (JEP) によると、この決定は JSM を使用しているプロジェクトが非常に少なかったために行われました。OpenSearch 3.0 は Java 21 にバンドルされており、まだ JSM の削除を強制されていませんが、非推奨でまもなく削除されるコンポーネントに依存し続けることは、長期的なサポートとイノベーションにとって持続不可能と判断されました。
2. **新しい JVM 機能、特にバーチャルスレッドとの非互換性**: [JEP 444](https://openjdk.org/jeps/444) で導入されたバーチャルスレッドは、モダン Java で最も期待されている機能の 1 つです。OpenSearch 3.0 は内部的にバーチャルスレッドを使用していませんが、プラグイン開発者や将来のバージョンの OpenSearch がスケーラビリティ向上のためにバーチャルスレッドを使用する可能性があると予想しています。しかし、Security Manager が有効な場合、バーチャルスレッドはパーミッションを引き継がないため、JSM ベースのセキュリティモデルとは事実上互換性がありません。したがって、JSM のサポートを継続すると、より優れた並行性とリソース効率を実現する重要な Java 機能の採用が妨げられることになります。

これらのニーズを踏まえ、OpenSearch 3.0 で JSM を非推奨にすることを決定しました。メジャーバージョンでこれを行うことで、変更を明確に伝え、後の 3.x マイナーリリースで破壊的なセキュリティ変更を導入することを避けることができました。

2021 年 12 月、OpenSearch コアリポジトリに代替手段のオプションを議論するための [Issue](https://github.com/opensearch-project/OpenSearch/issues/1687) が作成されました。JSM が Java プログラムに提供していた機能を直接置き換えるものがないことがすぐに明らかになりました。OpenSearch は、重要な JSM 機能を維持する代替手段を長期にわたって探索しました。

以下を含む多くの異なるオプションを検討しました。

1. プロセス外エクステンションによる [OpenSearch 拡張性](https://opensearch.org/blog/technical-roadmap-opensearch-extensibility/)への移行 (根本的な変更)
2. JVM を GraalVM に置き換える
3. `systemd` を使用したセキュリティ強化
4. 別の Java エージェントの導入
5. JSM と関連機能の完全な削除

## OpenSearch における JSM の役割の理解

OpenSearch の核心は、Apache Lucene 上に構築された強力な検索エンジンです。Lucene シャードに保存されたドキュメントにアクセスするための REST API レイヤーと、クラスター全体に分散されたノード上で Lucene を実行するための組み込みクラスター管理を提供します。OpenSearch はプラグイン可能なアーキテクチャを持ち、セキュリティ、オブザーバビリティ、インデックス管理などの追加機能を提供することでコア機能を拡張する多様なプラグインセットを備えています。OpenSearch プラグインは OpenSearch プロセスと同じ JVM 内で実行されますが、別のクラスローディングによって部分的に分離されています。OpenSearch はプラグインをデフォルトで安全とは見なしておらず、代わりに JSM に依存してプラグインをサンドボックス化し、明示的なクラスター管理者の承認なしに特権アクションを実行することを防いでいます。

JSM を使用する主なユーザーグループは、プラグイン開発者とクラスター管理者の 2 つです。これらのグループは異なる方法で JSM を使用します。

### プラグイン開発者による JSM の使用方法

特権アクションを実行するには、プラグイン開発者はアクションを実行するコードを `AccessController.doPrivileged(() -> { ... })` ブロックでラップし、`plugin-security.policy` ファイルで必要なパーミッションを付与する必要があります。JSM に関する一般的な不満は、プラグイン開発者が実行時まで何が `PrivilegedAction` を構成するかわからないことです。実行時に、プラグインが特定の操作 (例: ソケットへの接続やファイルシステムからの読み取り) を実行することが禁止されているというエラーが発生します。JSM は、`System.exit` などのシステム操作の呼び出しの防止から、リフレクションなどの他の Java 言語機能まで、幅広い制限を適用していました (JSM がカバーしていた領域の詳細については、[Permissions and Security Policy](https://docs.oracle.com/javase/8/docs/technotes/guides/security/spec/security-spec.doc3.html) を参照してください)。

プラグイン開発者は、ポリシーファイルでパーミッションを定義し、コードで特権アクションを実装することで JSM を使用します。

- 以下の `plugin-security.policy` ファイルの例は、プラグインが動作するために必要な基本的なパーミッションを定義しています。

  ```
  grant { 
    permission java.lang.RuntimePermission "shutdownHooks";
    permission java.lang.RuntimePermission "getClassLoader";
    permission java.lang.RuntimePermission "setContextClassLoader";
    permission java.util.PropertyPermission "*","read,write";
  }
  ```

- 以下は `AccessController.doPrivileged` ブロックの例です。この例では、`AccessController.doPrivileged(() -> { ... })` の呼び出しの前に `SpecialPermission.check()` が呼び出されています。OpenSearch では、`org.opensearch.SpecialPermission` は実行時にすべての JAR ファイル (コアとインストールされたプラグインの両方) に付与されます。このパーミッションは外部コード実行に対するセーフガードとして機能します。コールスタックに OpenSearch 外部のソース (例: API ペイロードから発生したコード) が含まれている場合、`SpecialPermission.check()` の呼び出しは失敗します。このメカニズムは、信頼されていないコードが OpenSearch プロセス内で特権アクションを実行することを防ぐのに役立ちます。

  ```java
  SpecialPermission.check();
  AccessController.doPrivileged((PrivilegedAction<Void>) () -> {
      if (Security.getProvider("BC") == null) {
          try {
              Class<?> providerClass = Class.forName("org.bouncycastle.jce.provider.BouncyCastleProvider");
              Provider provider = (Provider) providerClass.getDeclaredConstructor().newInstance();
              Security.addProvider(provider);
              log.debug("Bouncy Castle Provider added");
          } catch (Exception e) {
              log.debug("Bouncy Castle Provider could not be added", e);
          }
      }
      return null;
  });
  ```

### クラスター管理者による JSM の使用方法

クラスター管理者は、インストール時にプラグインが要求するパーミッションについてプロンプトが表示されます。以下の Security プラグインからのスニペットには、`BouncyCastle` プロバイダーの追加などのアクションをプラグインが実行できるようにするパーミッションが含まれています。

```console
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@     WARNING: plugin requires additional permissions     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
* java.io.FilePermission /proc/sys/net/core/somaxconn#plus read
* java.lang.RuntimePermission accessDeclaredMembers
```

## JSM を置き換えるためのソリューション

代替戦略を開発する際に、主要な JSM ユーザーインタラクションを理解することが重要でした。プラグイン開発者の特権操作のニーズと、管理者のパーミッション制御能力の両方を引き続きサポートするソリューションが必要でした。

JSM の代替候補を評価した結果、JSM が提供していたすべての機能を単一のアプローチで置き換えることはできないことが明らかになりました。OpenSearch コミュニティは、2 つの戦略を採用して JSM を置き換えることを決定しました。

1. **`systemd` ハードニング**: オペレーティングシステムの制御を使用した保護
2. **Java エージェント**: 特権操作をインターセプトして認可するための低レベルのインストルメンテーションの実装

### systemd ハードニング

代替戦略の最初のコンポーネントは `systemd` ハードニングで、`systemd` を init システムとして使用する Linux ディストリビューションで利用可能です。このアプローチは、以下のネイティブオペレーティングシステム機能を使用して OpenSearch プロセスをサンドボックス化します。

- **システムコール制限**: `seccomp` と `SystemCallFilter` ディレクティブを使用して、OpenSearch プロセスがアクセスできるカーネルインターフェースを制限します。
- **ファイルシステムパスの分離**: `ReadOnlyPaths`、`ReadWritePaths`、`InaccessiblePaths` を設定して、重要なシステムファイルへのアクセスを制御し、必要なディレクトリのみへの書き込みアクセスを制限します。
- **ケーパビリティ制限**: `CapabilityBoundingSet` を適用して、悪意のあるコードによって悪用される可能性のある `CAP_SYS_ADMIN` や `CAP_NET_ADMIN` などの危険な Linux ケーパビリティをブロックします。
- **プロセスの封じ込め**: `PrivateTmp`、`NoNewPrivileges`、`ProtectSystem` などのオプションを有効にして、特権昇格やファイルシステムの改ざんのリスクをさらに軽減します。

このアプローチは、OpenSearch プロセスが実行できるアクションを制限することで、悪意のあるプラグインからシステムを効果的に保護します。ただし、欠点は `systemd` ルールがプラグインレベルではなくプロセスレベルで適用されることです。これは、付与されたすべての特権が OpenSearch プロセス全体に影響することを意味し、JSM が提供していたきめ細かいプラグインごとの制御の適切な代替にはなりません。

### Java エージェント

代替戦略の 2 番目のコンポーネントはカスタム Java エージェントでした。Java エージェントは、アプリケーション実行前に JVM がロードするか、実行中にアタッチして、JVM がロードするすべてのクラスのバイトコードを表示、変換、または監視できる特別な JAR です。内部的には、Java 5 で導入された Instrumentation API に依存しています。Java エージェントは `-javaagent` Java 引数を通じて OpenSearch プロセスにアタッチされます。OpenSearch Java エージェントは、特権操作を監視し、実行中のコードベースに必要なパーミッションが明示的に付与されていることを確認するインターセプターで構成されています。Java エージェントの設定は JSM と一貫しています。`plugin-security.policy` ファイルが付与されたパーミッションのセットを定義し、プラグインのインストール時にクラスター管理者にプロンプトを表示します。

OpenSearch の Java エージェントは、ByteBuddy Instrumentation API を使用して、実行時に Java バイトコードをインターセプトしてインストルメントします。具体的には、エージェントは以下のような特権操作のインターセプターをインストールします。

- ソケットのオープンまたは接続
- ファイルの作成、読み取り、または書き込み

これらのインターセプターは、現在のコールスタックを検査して発信元のコードを特定し、既存の `plugin-security.policy` ファイルに基づいて必要なパーミッションが付与されているかどうかを評価します。これは既存の JSM モデルを反映しており、プラグイン開発者と管理者への影響を最小限に抑えています。

エージェントは JSM で以前サポートされていたすべてのパーミッションタイプ (例: リフレクションやスレッドコンテキストアクセス) をカバーしていませんが、最もセキュリティリスクの高いファイルおよびネットワークアクセスなどの最も機密性の高い操作に焦点を当てています。その他のセキュリティ制御は `systemd` を使用してオペレーティングシステムに委任されます。エージェントは拡張可能に設計されており、必要に応じてより多くのインターセプターを追加できます。

パフォーマンスと保守性の懸念から、過度のインストルメンテーションを避けることを特に選択しました。すべての可能なパーミッションチェックをインストルメントすると、パフォーマンスが大幅に低下し、過度に反復的なコードが必要になります。

## まとめ

JSM の非推奨化は、Java エコシステムと OpenSearch の両方にとって重要な転換点です。JSM が提供していた機能を完全に複製できる単一のソリューションはありませんが、OpenSearch の 2 つのアプローチ (`systemd` によるオペレーティングシステムレベルの保護と、プラグインレベルのアクセス制御のための軽量な Java エージェントの導入) は、プラットフォームを保護するための堅牢で拡張可能な基盤を提供します。

このアプローチにより、OpenSearch はユーザーが依存する拡張性とプラグインエコシステムを維持しながら、安全でパフォーマンスが高く、進化する Java エコシステムと互換性を保つことができます。
