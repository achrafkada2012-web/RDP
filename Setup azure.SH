#!/usr/bin/env bash
# يتطلب Azure CLI وتسجيل الدخول: az login
set -euo pipefail

RG="rg-winpc"
VM="winpc"
LOCATION="westeurope"          # غيّره لأقرب منطقة لك
SIZE="Standard_D2s_v5"         # 2 vCPU / 8GB
ADMIN_USER="azureadmin"
ADMIN_PASS="${ADMIN_PASS:?اضبط ADMIN_PASS (12 حرفًا على الأقل مع أرقام ورموز)}"
MY_IP="${MY_IP:?اضبط MY_IP (عنوان IP الخاص بك) لتقييد RDP}"

az group create -n "$RG" -l "$LOCATION"

# قرص النظام 150GB
az vm create \
  -g "$RG" -n "$VM" \
  --image MicrosoftWindowsServer:WindowsServer:2022-datacenter-azure-edition:latest \
  --size "$SIZE" \
  --os-disk-size-gb 150 \
  --storage-sku StandardSSD_LRS \
  --admin-username "$ADMIN_USER" \
  --admin-password "$ADMIN_PASS" \
  --public-ip-sku Standard \
  --nsg-rule NONE

# السماح بـ RDP من عنوانك فقط
az network nsg rule create \
  -g "$RG" --nsg-name "${VM}NSG" -n allow-rdp-me \
  --priority 1000 --direction Inbound --access Allow --protocol Tcp \
  --destination-port-ranges 3389 --source-address-prefixes "$MY_IP"

# حساب خدمة للبوت بصلاحية محصورة في مجموعة الموارد
SUB_ID=$(az account show --query id -o tsv)
az ad sp create-for-rbac \
  --name "winpc-discord-bot" \
  --role Contributor \
  --scopes "/subscriptions/$SUB_ID/resourceGroups/$RG"

echo
echo "ضع القيم أعلاه في ملف .env: appId=CLIENT_ID, password=CLIENT_SECRET, tenant=TENANT_ID"
echo "SUBSCRIPTION_ID=$SUB_ID"
echo "اسم عنوان IP العام عادةً: ${VM}PublicIP"