# بوت ديسكورد

## الأوامر
| الأمر | الوظيفة |
|---|---|
| `/ping` | فحص أن البوت يعمل |
| `/build` | تشغيل workflow `build.yml` على GitHub (للمسموح لهم فقط) |

## التشغيل
```bash
cp .env.example .env     # عبّئ القيم
pip install -r requirements.txt
python bot.py
```

## الإعداد
1. أنشئ بوتًا من https://discord.com/developers/applications ← Bot ← Reset Token.
2. أضفه لسيرفرك من OAuth2 ← URL Generator (Scopes: `bot` و`applications.commands`).
3. ضع معرفك في `ALLOWED_USER_IDS` (Developer Mode ← Copy User ID).
4. لأمر `/build` فقط: أنشئ GitHub fine-grained token بصلاحية **Actions: Read and write** على المستودع.

## ملاحظات
- التوكنات تُوضع في `.env` فقط، ولا يُرفع إلى GitHub.
- الردود ephemeral (تظهر لك وحدك).nstall -r requirements.txt
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