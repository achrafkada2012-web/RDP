# جهاز Windows سحابي + بوت ديسكورد

## الخطوات

1. **أنشئ الجهاز على Azure**
   ```bash
   az login
   export ADMIN_PASS='ضع-كلمة-مرور-قوية-1!'
   export MY_IP='x.x.x.x'      # عنوان IP العام لجهازك
   bash setup_azure.sh
   ```
   ينشئ جهاز Windows Server 2022 بقرص نظام **150GB**، ويسمح بـ RDP من عنوانك فقط،
   ويطبع بيانات حساب الخدمة للبوت.

2. **أنشئ بوت ديسكورد**
   - https://discord.com/developers/applications → New Application → Bot → انسخ Token.
   - من OAuth2 → URL Generator اختر `bot` و`applications.commands` وأضفه لسيرفرك.
   - فعّل Developer Mode في ديسكورد وانسخ معرفك (Copy User ID) إلى `ALLOWED_USER_IDS`.

3. **شغّل البوت**
   ```bash
   cp .env.example .env     # عبّئ القيم
   pip install -r requirements.txt
   python bot.py
   ```

4. **الاتصال من تطبيق Windows App**
   - أرسل `/start` في ديسكورد، ثم احصل على العنوان.
   - في Windows App: `+` ← Add PC ← أدخل العنوان ← اسم المستخدم `azureadmin` وكلمة المرور.
   - عند الانتهاء أرسل `/stop` حتى تتوقف الفوترة (الجهاز يُحرَّر، ويبقى القرص فقط بتكلفة تخزين).

## الأوامر
| الأمر | الوظيفة |
|---|---|
| `/start` | تشغيل الجهاز وعرض العنوان |
| `/stop` | إيقاف وتحرير الجهاز |
| `/status` | حالة الجهاز |
| `/ip` | عنوان الاتصال |
| `/build` | تشغيل workflow `build.yml` على GitHub |

## ملاحظات
- الردود كلها ephemeral (تظهر لك وحدك) حتى لا يُكشف العنوان.
- العنوان ديناميكي ويتغير بعد كل `/stop` ثم `/start`، فاستخدم `/ip`.
- إن تغيّر عنوان IP الخاص بك عدّل قاعدة NSG `allow-rdp-me`.
- لأمر `/build` أنشئ GitHub fine-grained token بصلاحية **Actions: Read and write** على المستودع فقط.
- التكلفة تعتمد على الحجم والمنطقة؛ راجع تسعيرة Azure وفعّل تنبيه ميزانية.
- لا ترفع ملف `.env` إلى GitHub أبدًا.