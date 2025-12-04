# OpenSearch Blog Japanese Translation

This project translates articles from the [OpenSearch Project Blog](https://opensearch.org/blog/) into Japanese and publishes them on [Zenn](https://zenn.dev/opensearch).

## Publication

https://zenn.dev/opensearch

## Local Development

```bash
npm install
npx zenn preview
```

## Setup

### Prerequisites

- [Kiro CLI](https://kiro.dev/) installed
- Node.js (npm)
- git, curl

### Installing Kiro CLI

macOS:
```bash
curl -fsSL https://cli.kiro.dev/install | bash
```

Ubuntu:
```bash
wget https://desktop-release.q.us-east-1.amazonaws.com/latest/kiro-cli.deb
sudo dpkg -i kiro-cli.deb
```

For other Linux distributions, see the [official documentation](https://kiro.dev/docs/cli/installation/).

### Environment Variables

The following environment variables are required to run translation tasks.

| Variable | Description |
| --- | --- |
| `GITHUB_TOKEN` | GitHub API authentication token |

### Repository Settings

It is recommended to enable "Automatically delete head branches" in Settings > General > Pull Requests.

## Running Translations

```bash
.kiro/commands/translate-opensearch-blog.sh <article-url>
```

To translate multiple articles at once:

```bash
.kiro/commands/translate-opensearch-blog.sh <URL1> <URL2> ...
```

## Contributing

Please submit translation requests via [Issues](../../issues).
