# المعلّم AlMuallim

المعلّم مدرب محلي بالعربية لتعلم البرمجة والأمن بالتفكيك: يحلل ملفات Python عبر AST، يشرح الرموز والدوال، يولد أسئلة، ويحوّل CVE/NVD إلى دروس أمنية منظمة.

## آلية العمل

1. `teach-python` يقرأ ملف Python ويستخرج imports/classes/functions والتعقيد التقريبي.
2. `lesson_from_analysis` يحول الخريطة إلى درس عربي مع أسئلة مراجعة.
3. `convert-nvd` يحول بيانات CVE إلى دروس أمنية فيها concept/severity/exercise/quiz.
4. `batch/stress` يتحققان من اكتمال الدروس وجودة الحقول وعدم الانهيار.

## تشغيل سريع

```powershell
python -m almuallim.cli teach-python --path almuallim\analyzer.py
python -m almuallim.cli convert-nvd --input C:\Projects\kashif\data\external\nvd_cves_12000.jsonl
python -m almuallim.cli batch --input data\benchmarks\almuallim_nvd_lessons.jsonl
```

## بيانات اختبار كبيرة

المصدر: NVD CVE API 2.0 المحفوظ عبر مشروع كاشف بعدد 12,000 سجل.

## آخر نتائج

- الاختبارات الذاتية: 3/3 ناجحة.
- تحويل NVD: 12,000 درس أمني، منها HIGH=5,319 وCRITICAL=56.
- Benchmark: 12,000 فحص، quality=100%، missing=0، errors=0، p99=0.0019ms.
- Stress: 36,000 فحص، quality=100%، errors=0، p99=0.0025ms، peak memory=1.18MB.

## تحسينات إنتاجية 2026-07-04

- الدرس الناتج من Python لا يعتمد على نص حر فقط؛ يستخدم AST لاستخراج الدوال/classes/imports والتعقيد التقريبي.
- دروس NVD لها schema ثابت (`title/level/concept/summary_ar/exercise/quiz`) حتى يسهل اختبارها وتشغيلها في واجهة تعليمية لاحقاً.
- batch/stress يتحققان من اكتمال schema وعدد الأسئلة بدل الاكتفاء بعدّ السجلات.

## التشغيل المؤسسي (Enterprise) — v1.0.0

- **خدمة دروس HTTP**: `python -m almuallim.cli serve` → `POST /api/teach {"code"} أو {"path"}` يعيد درساً عربياً + quiz (تحليل AST بلا أي تنفيذ).
- **نقاط فحص**: `/api/health` (مفتوح) · `/api/version` · `/api/metrics`.
- **تهيئة عبر البيئة**: متغيرات `ALMUALLIM_*` — انظر `docs/OPERATIONS.md`.
- **مصادقة**: `ALMUALLIM_API_KEY` → ترويسة `X-API-Key`. **سجلات JSON**: `logs\almuallim.service.jsonl`.
