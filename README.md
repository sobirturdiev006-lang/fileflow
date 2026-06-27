# FileFlow

Excel va PDF fayllarni qayta ishlash uchun backend xizmati. Django + DRF + Celery + Redis + PostgreSQL asosida qurilgan, asinxron fayl processing'ni namoyish etadi.

## Imkoniyatlari

- **Excel tozalash / deduplikatsiya** — bo'sh qatorlarni va takrorlangan qatorlarni o'chirish (barcha ustunlar bo'yicha yoki tanlangan ustunlar bo'yicha)
- **Excel → PDF hisobot** — Excel ma'lumotlaridan formatlangan PDF jadval yaratish
- **PDF jadval → Excel** — PDF ichidagi jadvallarni topib, Excel faylga ajratib chiqarish

Har bir operatsiya **Celery** orqali asinxron bajariladi — foydalanuvchi fayl yuklab, natijani "job status" orqali kuzatib boradi.

## Texnologiyalar

| Qatlam | Texnologiya |
|---|---|
| Backend | Django, Django REST Framework |
| Asinxron ishlov | Celery + Redis |
| Ma'lumotlar bazasi | PostgreSQL (lokal sinov uchun SQLite ham qo'llab-quvvatlanadi) |
| Fayl ishlov | pandas, openpyxl, pdfplumber, reportlab |
| Frontend | Django Templates + vanilla JS (fetch API) |
| Konteynerizatsiya | Docker, docker-compose |

## Loyiha tuzilishi

```
fileflow/
├── config/             # Django sozlamalari, URL routing, Celery konfiguratsiyasi
├── files/               # Asosiy ilova: models, serializers, views, tasks, services
│   ├── models.py        # ProcessingJob modeli
│   ├── serializers.py
│   ├── services.py      # Fayllarni qayta ishlash logikasi
│   ├── tasks.py         # Celery task'lar
│   ├── views.py         # DRF ViewSet (API)
│   └── frontend_views.py # Template view
├── templates/           # HTML shablonlar
├── static/              # CSS, JS
└── media/               # Yuklangan va natija fayllar (gitignore'da)
```

## API endpoint'lari

| Method | Endpoint | Tavsif |
|---|---|---|
| `POST` | `/api/jobs/` | Fayl yuklash, job yaratish, Celery task ishga tushirish |
| `GET` | `/api/jobs/` | Barcha joblar ro'yxati |
| `GET` | `/api/jobs/{id}/` | Bitta job holati va natijasi |

`job_type` qiymatlari: `excel_clean`, `excel_to_pdf`, `pdf_table_extract`

## O'rnatish va ishga tushirish

### Variant A — Docker bilan (tavsiya etiladi)

```bash
git clone https://github.com/<username>/fileflow.git
cd fileflow
cp .env.example .env   # kerakli qiymatlarni to'ldiring
docker-compose up --build
```

Brauzerda: `http://localhost:8000/`

### Variant B — Lokal (Docker'siz)

```bash
git clone https://github.com/<username>/fileflow.git
cd fileflow
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
```

`.env` faylida:
```
USE_SQLITE=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

Redis lokal ishlab turgan bo'lishi kerak (masalan `docker run -d -p 6379:6379 redis`).

```bash
python manage.py migrate
python manage.py runserver
```

Boshqa terminalda Celery worker:
```bash
celery -A config worker -l info --pool=solo   # Windows uchun --pool=solo shart
```

## Kelajakdagi rejalar

- [ ] Foydalanuvchi autentifikatsiyasi (job'larni user bilan bog'lash)
- [ ] Fayl turi/hajmi bo'yicha kengaytirilgan validatsiya
- [ ] Pagination va filtrlash (job ro'yxati uchun)
- [ ] Production uchun Gunicorn + Nginx konfiguratsiyasi

## Muallif

Junior Backend Developer — Python/Django/DRF stack'ni mustahkamlash maqsadida qurilgan portfolio loyihasi.