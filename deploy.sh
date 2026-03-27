#!/usr/bin/env bash
# ============================================================
#  DocSimplify – Azure Infrastructure Deploy
#  Ejecutar desde Git Bash en Windows o WSL
#  Uso: bash deploy.sh
# ============================================================
set -euo pipefail

SUBSCRIPTION_ID="f113a4a0-b4f8-4c7c-96a7-ab4a289ef9bb"
RESOURCE_GROUP="rg-draftdemo"
LOCATION="eastus"
DEPLOYMENT_NAME="docsimplify-deploy"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="$(basename "$SCRIPT_DIR")"

echo "============================================"
echo "  DocSimplify – Azure Deploy"
echo "  Suscripción : $SUBSCRIPTION_ID"
echo "  Grupo       : $RESOURCE_GROUP"
echo "  Región      : $LOCATION"
echo "============================================"
echo ""

# ── 0. Instalar extensión az search si falta ────────────────────────────────
echo "[0/7] Verificando extensión azure-search..."
az extension add --name azure-search --only-show-errors 2>/dev/null || true
echo "      OK"

# ── 1. Seleccionar suscripción ───────────────────────────────────────────────
echo "[1/7] Configurando suscripción..."
az account set --subscription "$SUBSCRIPTION_ID"
echo "      OK"

# ── 2. Crear resource group ──────────────────────────────────────────────────
echo "[2/7] Creando resource group '$RESOURCE_GROUP'..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none
echo "      OK"

# ── 3. Desplegar Bicep ───────────────────────────────────────────────────────
echo "[3/7] Desplegando infraestructura (puede tomar 8-12 min)..."
az deployment group create \
  --name "$DEPLOYMENT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --template-file "$SCRIPT_DIR/infra/main.bicep" \
  --parameters location="$LOCATION" \
  --output none
echo "      OK"

# ── 4. Leer outputs del deployment ──────────────────────────────────────────
echo "[4/7] Leyendo outputs..."

get_output() {
  az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.outputs.$1.value" \
    --output tsv
}

FOUNDRY_NAME=$(get_output "foundryName")
FOUNDRY_ENDPOINT=$(get_output "foundryEndpoint")
AI_PROJECT_NAME=$(get_output "aiProjectName")
STORAGE_ACCOUNT=$(get_output "storageAccountName")
COSMOS_ENDPOINT=$(get_output "cosmosEndpoint")
COSMOS_ACCOUNT=$(get_output "cosmosAccountName")
SEARCH_ENDPOINT=$(get_output "searchEndpoint")
SEARCH_SERVICE=$(get_output "searchServiceName")
DOC_INTEL_ENDPOINT=$(get_output "docIntelEndpoint")
DOC_INTEL_NAME=$(get_output "docIntelName")

# Construir AI Project endpoint
# Quitar trailing slash y agregar ruta del proyecto
FOUNDRY_BASE="${FOUNDRY_ENDPOINT%/}"
AI_PROJECT_ENDPOINT="${FOUNDRY_BASE}/api/projects/${AI_PROJECT_NAME}"

echo "      Foundry   : $FOUNDRY_NAME"
echo "      Proyecto  : $AI_PROJECT_NAME"
echo "      Cosmos    : $COSMOS_ACCOUNT"
echo "      Search    : $SEARCH_SERVICE"
echo "      DocIntel  : $DOC_INTEL_NAME"

# ── 5. Obtener claves/secrets ────────────────────────────────────────────────
echo "[5/7] Obteniendo claves..."

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name "$FOUNDRY_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "key1" --output tsv)

STORAGE_CONN=$(az storage account show-connection-string \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query "connectionString" --output tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name "$COSMOS_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --query "primaryMasterKey" --output tsv)

SEARCH_KEY=$(az search admin-key show \
  --service-name "$SEARCH_SERVICE" \
  --resource-group "$RESOURCE_GROUP" \
  --query "primaryKey" --output tsv)

DOC_INTEL_KEY=$(az cognitiveservices account keys list \
  --name "$DOC_INTEL_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "key1" --output tsv)

echo "      OK (claves obtenidas)"

# ── 6. Crear blob container ──────────────────────────────────────────────────
echo "[6/7] Creando contenedor blob 'documents'..."
az storage container create \
  --name "documents" \
  --connection-string "$STORAGE_CONN" \
  --output none
echo "      OK"

# ── 7. Generar .env ──────────────────────────────────────────────────────────
echo "[7/7] Generando .env..."

# Usamos printf para evitar que caracteres especiales del connection string
# (;  =  +  /) rompan el heredoc
ENV_FILE="$SCRIPT_DIR/.env"

printf '%s\n' \
  "# ── Azure AI Foundry / Agent Framework ──────────────────────────────────────" \
  "AI_PROJECT_ENDPOINT=${AI_PROJECT_ENDPOINT}" \
  "AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini" \
  "" \
  "# ── Azure OpenAI (embeddings + completions) ──────────────────────────────────" \
  "OPENAI_ENDPOINT=${FOUNDRY_BASE}" \
  "OPENAI_API_KEY=${OPENAI_KEY}" \
  "OPENAI_EMBEDDING_MODEL=text-embedding-ada-002" \
  "" \
  "# ── JWT Authentication ───────────────────────────────────────────────────────" \
  "JWT_SECRET_KEY=docsimplify-hackaton-2026-secret-key" \
  "JWT_ALGORITHM=HS256" \
  "JWT_EXPIRE_MINUTES=60" \
  "" \
  "# ── Azure Blob Storage ───────────────────────────────────────────────────────" \
  "AZURE_STORAGE_CONNECTION_STRING=${STORAGE_CONN}" \
  "AZURE_STORAGE_CONTAINER=documents" \
  "" \
  "# ── Azure Cosmos DB ──────────────────────────────────────────────────────────" \
  "COSMOS_ENDPOINT=${COSMOS_ENDPOINT}" \
  "COSMOS_KEY=${COSMOS_KEY}" \
  "COSMOS_DATABASE=docsimplify" \
  "COSMOS_USERS_CONTAINER=users" \
  "COSMOS_DOCUMENTS_CONTAINER=documents" \
  "COSMOS_CHATS_CONTAINER=chats" \
  "" \
  "# ── Azure AI Search (RAG) ────────────────────────────────────────────────────" \
  "AZURE_SEARCH_ENDPOINT=${SEARCH_ENDPOINT}" \
  "AZURE_SEARCH_KEY=${SEARCH_KEY}" \
  "AZURE_SEARCH_INDEX=documents-index" \
  "" \
  "# ── Azure Document Intelligence ──────────────────────────────────────────────" \
  "DOCUMENT_INTELLIGENCE_ENDPOINT=${DOC_INTEL_ENDPOINT}" \
  "DOCUMENT_INTELLIGENCE_KEY=${DOC_INTEL_KEY}" \
  "" \
  "# ── General ──────────────────────────────────────────────────────────────────" \
  "ENVIRONMENT=development" \
  > "$ENV_FILE"

echo ""
echo "============================================"
echo "  ✅ Deploy completado exitosamente"
echo "============================================"
echo ""
echo "  Resource Group : $RESOURCE_GROUP"
echo "  AI Foundry     : $FOUNDRY_NAME"
echo "  AI Project     : $AI_PROJECT_NAME"
echo "  Cosmos DB      : $COSMOS_ACCOUNT"
echo "  AI Search      : $SEARCH_SERVICE"
echo "  Storage        : $STORAGE_ACCOUNT"
echo "  Doc Intel      : $DOC_INTEL_NAME"
echo ""
echo "  .env generado automaticamente en el proyecto."
echo ""
echo "  Para iniciar el backend:"
echo "    cd $PROJECT_NAME"
echo "    uvicorn src.main:app --reload"
echo ""
