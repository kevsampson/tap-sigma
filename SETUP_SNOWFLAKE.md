# Setting up tap-sigma with Snowflake

This guide will help you extract data from Sigma Computing and load it into Snowflake using Meltano.

## Prerequisites

- Python 3.8 or higher
- Snowflake account with appropriate permissions
- Sigma Computing API credentials (Client ID and Secret)

## Installation

### 1. Install Meltano

```bash
pip install meltano
```

### 2. Initialize Meltano Project (if needed)

```bash
meltano init my-sigma-project
cd my-sigma-project
```

### 3. Add tap-sigma

```bash
# Install directly from GitHub
meltano add extractor tap-sigma --from-ref https://github.com/YOUR_USERNAME/tap-sigma.git
```

Or add to your `meltano.yml`:

```yaml
extractors:
  - name: tap-sigma
    namespace: tap_sigma
    pip_url: git+https://github.com/YOUR_USERNAME/tap-sigma.git
    config:
      client_id: ${SIGMA_CLIENT_ID}
      client_secret: ${SIGMA_CLIENT_SECRET}
      api_url: https://api.us.azure.sigmacomputing.com
```

### 4. Add Snowflake Loader

```bash
meltano add loader target-snowflake
```

Or add to your `meltano.yml`:

```yaml
loaders:
  - name: target-snowflake
    variant: transferwise
    pip_url: pipelinewise-target-snowflake
    config:
      account: ${SNOWFLAKE_ACCOUNT}
      dbname: ${SNOWFLAKE_DATABASE}
      user: ${SNOWFLAKE_USER}
      password: ${SNOWFLAKE_PASSWORD}
      warehouse: ${SNOWFLAKE_WAREHOUSE}
      schema: ${SNOWFLAKE_SCHEMA}
      default_target_schema: sigma_data
```

## Configuration

### Environment Variables

Create a `.env` file in your Meltano project:

```bash
# Sigma Computing API
SIGMA_CLIENT_ID=your-client-id
SIGMA_CLIENT_SECRET=your-client-secret

# Snowflake
SNOWFLAKE_ACCOUNT=your-account.region.cloud
SNOWFLAKE_DATABASE=ANALYTICS
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_SCHEMA=PUBLIC
```

### Alternative: Configure without Meltano

You can also use the tap directly with any Singer target:

```bash
# Install tap-sigma
pip install git+https://github.com/YOUR_USERNAME/tap-sigma.git

# Install target-snowflake
pip install pipelinewise-target-snowflake

# Create config files
cat > tap-config.json <<EOF
{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "api_url": "https://api.us.azure.sigmacomputing.com"
}
EOF

cat > target-config.json <<EOF
{
  "account": "your-account.region.cloud",
  "dbname": "ANALYTICS",
  "user": "your-username",
  "password": "your-password",
  "warehouse": "COMPUTE_WH",
  "schema": "SIGMA_DATA"
}
EOF

# Run the pipeline
tap-sigma --config tap-config.json --discover > catalog.json
tap-sigma --config tap-config.json --catalog catalog.json | target-snowflake --config target-config.json
```

## Running the Pipeline

### With Meltano

```bash
# Run a full sync
meltano run tap-sigma target-snowflake

# Schedule regular syncs
meltano schedule add sigma-daily --job tap-sigma-to-snowflake --interval "@daily"
```

### Incremental Sync

The tap supports state management for incremental syncs:

```bash
meltano run tap-sigma target-snowflake --state-id sigma-prod
```

## Available Streams

The tap extracts the following data from Sigma Computing:

| Stream | Description | Primary Key |
|--------|-------------|-------------|
| `connections` | Data warehouse connections | connectionId |
| `datasets` | Sigma datasets | datasetId |
| `members` | Organization members | memberId |
| `teams` | Teams | teamId |
| `files` | Files and folders | inodeId |
| `workbooks` | Workbooks | workbookId |
| `workbook_pages` | Pages within workbooks | workbookId, pageId |
| `tags` | Version tags | tagId |
| `user_attributes` | Custom user attributes | userAttributeId |
| `whoami` | Current user info | memberId |

## Snowflake Schema

Data will be loaded into tables matching the stream names:

- `SIGMA_DATA.CONNECTIONS`
- `SIGMA_DATA.DATASETS`
- `SIGMA_DATA.MEMBERS`
- `SIGMA_DATA.TEAMS`
- `SIGMA_DATA.FILES`
- `SIGMA_DATA.WORKBOOKS`
- `SIGMA_DATA.WORKBOOK_PAGES`
- `SIGMA_DATA.TAGS`
- `SIGMA_DATA.USER_ATTRIBUTES`
- `SIGMA_DATA.WHOAMI`

## Selecting Specific Streams

To sync only specific streams, create a custom `catalog.json`:

```bash
# Discover all streams
tap-sigma --config tap-config.json --discover > catalog.json

# Edit catalog.json and set "selected": true for desired streams
# Then run with the modified catalog
tap-sigma --config tap-config.json --catalog catalog.json | target-snowflake --config target-config.json
```

Or with Meltano:

```bash
# Select specific streams
meltano select tap-sigma connections datasets workbooks

# Verify selection
meltano select tap-sigma --list

# Run selected streams only
meltano run tap-sigma target-snowflake
```

## Troubleshooting

### Authentication Errors

If you see authentication errors, verify:
1. Client ID and Secret are correct
2. API URL matches your Sigma instance (AWS, Azure, or GCP)
3. Credentials have appropriate API access permissions

### Connection Timeouts

For large datasets, you may need to adjust Snowflake warehouse size:

```yaml
loaders:
  - name: target-snowflake
    config:
      warehouse: LARGE_WH  # Use a larger warehouse
```

### Rate Limiting

The tap implements automatic retry with exponential backoff. If you encounter rate limits:
- The authentication endpoint is limited to 1 request/second
- Standard endpoints should handle normal load
- Export endpoints are limited to 100 requests/minute

## Support

For issues specific to:
- **tap-sigma**: Open an issue on GitHub
- **Sigma Computing API**: Contact Sigma support
- **Snowflake**: Check Snowflake documentation
- **Meltano**: Visit https://docs.meltano.com

## Example Analytics Queries

Once data is in Snowflake, you can run queries like:

```sql
-- Most active workbooks by update frequency
SELECT
    name,
    updated_at,
    created_by,
    COUNT(*) OVER (PARTITION BY created_by) as workbooks_by_creator
FROM sigma_data.workbooks
ORDER BY updated_at DESC
LIMIT 10;

-- Dataset usage across connections
SELECT
    c.name as connection_name,
    COUNT(d.dataset_id) as dataset_count
FROM sigma_data.connections c
LEFT JOIN sigma_data.datasets d ON c.connection_id = d.connection_id
GROUP BY c.name
ORDER BY dataset_count DESC;

-- Team membership overview
SELECT
    t.name as team_name,
    COUNT(m.member_id) as member_count
FROM sigma_data.teams t
LEFT JOIN sigma_data.members m ON 1=1  -- Adjust based on your team membership structure
GROUP BY t.name;
```
