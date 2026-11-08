import datetime
import json
from app.database import Base, engine, SessionLocal
from app.models import AdminUser, TherapistProfile, AppointmentRequest, Article
from app.auth import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Admin User
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            pw_hash, salt = hash_password("psychologist2026")
            admin = AdminUser(
                username="admin",
                password_hash=pw_hash,
                salt=salt,
                role="admin"
            )
            db.add(admin)
            print("Created default admin user: admin / psychologist2026")

        # 2. Therapist Profile
        profile = db.query(TherapistProfile).first()
        if not profile:
            profile = TherapistProfile()
            db.add(profile)

        profile.name_en = "Dr. Hassan Agha Nasiri"
        profile.name_fa = "دکتر حسن آقانصیری"
        profile.title_en = "Licensed Clinical Psychologist & Existential Psychotherapist (PhD)"
        profile.title_fa = "دکترای تخصصی روانشناسی بالینی و روان‌درمانگر اگزیستانسیال"
        profile.bio_en = (
            "Dr. Hassan Agha Nasiri is a licensed clinical psychologist, researcher, and existential psychotherapist "
            "with over 12 years of clinical experience. Founder of Dasein Journal, Dr. Agha Nasiri integrates "
            "Existential Psychotherapy, Cognitive Behavioral Therapy (CBT), and Acceptance & Commitment Therapy (ACT) "
            "to guide clients through emotional suffering, identity crises, anxiety, and the search for authentic meaning."
        )
        profile.bio_fa = (
            "دکتر حسن آقانصیری، روانشناس بالینی، پژوهشگر و روان‌درمانگر اگزیستانسیال، با بیش از ۱۲ سال تجربه بالینی و بنیان‌گذار "
            "ژورنال دازاین (Dasein Journal). رویکرد درمانی ایشان تلفیقی از روان‌درمانی اگزیستانسیال، درمان شناختی‌رفتاری (CBT) و "
            "پذیرش و تعهد (ACT) است که فضایی ژرف، امن و همدلانه برای رویارویی با تعارضات وجودی، درمان اضطراب و بازیافتن معنای اصیل زیستن فراهم می‌آورد."
        )
        profile.specializations_en_json = json.dumps([
            "Existential & Meaning-Centered Therapy",
            "Anxiety, Panic & Existential Dread",
            "Depression & Emotional Numbness",
            "Couples & Intimate Relational Healing",
            "Trauma, Grief & Loss Processing",
            "Identity, Life Transitions & Authenticity"
        ], ensure_ascii=False)
        profile.specializations_fa_json = json.dumps([
            "روان‌درمانی اگزیستانسیال و معنادرمانی",
            "درمان اضطراب، وسواس و بحران‌های وجودی",
            "افسردگی و بازیابی سرزندگی روانی",
            "زوج‌درمانی و بهبود صمیمیت عاطفی",
            "درمان تروما، سوگ و بحران فقدان",
            "بحران‌های هویتی و اصالت فردی"
        ], ensure_ascii=False)
        profile.credentials_en_json = json.dumps([
            "Ph.D. in Clinical Psychology",
            "Licensed Clinical Psychologist (Reg #18420)",
            "Founder & Editor of Dasein Journal",
            "Certified CBT, ACT & Existential Psychotherapist",
            "Member of International Association for Relational Psychoanalysis",
            "Over 12 Years of Clinical & Academic Practice"
        ], ensure_ascii=False)
        profile.credentials_fa_json = json.dumps([
            "دکترای تخصصی روانشناسی بالینی",
            "عضو رسمی سازمان نظام روانشناسی و مشاوره ایران (شماره پروانه: ۱۸۴۲۰)",
            "بنیان‌گذار و مدیر علمی ژورنال دازاین (Dasein Journal)",
            "گواهینامه تخصصی روان‌درمانی اگزیستانسیال و شناختی-رفتاری",
            "عضو انجمن علمی روانشناسی بالینی",
            "بیش از ۱۲ سال سابقه درمان و پژوهش بالینی"
        ], ensure_ascii=False)
        profile.years_experience = 12
        profile.email = "contact@daseinjournal.com"
        profile.phone = "+989125197973"
        profile.telegram_url = "https://t.me/dasein_journal"
        profile.instagram_url = "https://instagram.com/dasein.journal"
        profile.address_en = "Suite 402, North Kargar Ave, Tehran / Online Worldwide via Zoom & Google Meet"
        profile.address_fa = "تهران، خیابان کارگر شمالی، نبش کوچه یازدهم، ساختمان پزشکان، طبقه ۴، واحد ۴۰۲ / جلسات آنلاین در سراسر دنیا"
        profile.photo_url = "/static/images/dr-hassan-aghanasiri.jpg"
        print("Configured therapist profile for Dr. Hassan Agha Nasiri (Dasein Journal)")

        # 3. Initial Articles (Bilingual)
        if db.query(Article).count() == 0:
            articles = [
                Article(
                    slug="understanding-anxiety-nervous-system-grounding",
                    title_en="Understanding Anxiety: Why Your Nervous System Reacts and How to Ground It",
                    title_fa="درک اضطراب: چرا سیستم عصبی ما واکنش نشان می‌دهد و چگونه به آرامش برسیم؟",
                    excerpt_en="Anxiety is not a character flaw—it is a survival mechanism of the autonomic nervous system. Learn how to recognize somatic triggers and cultivate soothing anchors.",
                    excerpt_fa="اضطراب نقص در شخصیت نیست، بلکه سازوکار کهن سیستم عصبی خودمختار برای محافظت از ماست. راهکارهای علمی برای بازگرداندن سیستم عصبی به حالت ایمن را بیاموزید.",
                    content_en=(
                        "## The Biology of the Anxious Response\n\n"
                        "When your brain perceives a potential threat—whether it is a difficult conversation, work burnout, "
                        "or financial uncertainty—the amygdala sounds an alarm. Your sympathetic nervous system triggers the "
                        "classic 'fight, flight, or freeze' cascade: heart rate increases, breathing becomes shallow, and thoughts race.\n\n"
                        "In therapy, our first step is normalizing this bodily response. You are not 'broken'; your alarm system is "
                        "simply oversensitive.\n\n"
                        "### 3 Concrete Grounding Techniques\n\n"
                        "1. **The 4-7-8 Breathing Cycle**: Inhale quietly through your nose for 4 counts, hold for 7, and exhale completely "
                        "through your mouth with a whoosh sound for 8. Repeat for 4 cycles to stimulate the vagus nerve.\n"
                        "2. **5-4-3-2-1 Sensory Reset**: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.\n"
                        "3. **Cognitive Defusion**: Instead of saying 'I am going to fail', reframe it as: 'I notice my mind is offering me the thought that I might fail.'"
                    ),
                    content_fa=(
                        "## زیست‌شناسی واکنش اضطرابی\n\n"
                        "هنگامی که مغز تهدیدی را ادراک می‌کند—خواه یک گفتگوی دشوار کاری باشد یا نگرانی‌های مالی—بخش آمیگدال زنگ خطر را به صدا "
                        "درمی‌آورد. سیستم عصبی سمپاتیک وارد حالت «جنگ، گریز یا انجماد» می‌شود: ضربان قلب بالا می‌رود، تنفس سطحی می‌شود و "
                        "نشخوار فکری اوج می‌گیرد.\n\n"
                        "در روان‌درمانی، گام نخست عادی‌سازی این واکنش بدنی است. شما دچار نقص نیستید؛ بلکه سیستم هشدار شما نیازمند تنظیم مجدد است.\n\n"
                        "### ۳ تکنیک ملموس برای آرام‌سازی و رهایی از تنش\n\n"
                        "۱. **الگوی تنفس آرام‌بخش (۴-۷-۸)**: به مدت ۴ شماره از بینی دم بگیرید، ۷ شماره نفس را نگه دارید و در ۸ شماره به آرامی از دهان بازدم کنید. این الگو عصب واگ را فعال می‌کند.\n"
                        "۲. **تکنیک حسی ۵-۴-۳-۲-۱**: ۵ شیء را ببینید، ۴ حس لامسه را لمس کنید، ۳ صدا را بشنوید، ۲ بو را حس کنید و ۱ طعم را مزمزه کنید تا ذهن به زمان حال بازگردد.\n"
                        "۳. **جداسازی شناختی**: به جای گفتن «من در این کار شکست می‌خورم»، به خود بگویید: «من متوجه هستم که ذهنم در حال تولید فکر شکست است»."
                    ),
                    category="Anxiety & Stress",
                    read_time=6,
                    featured_image="/static/images/article-anxiety.svg",
                    published=True
                ),
                Article(
                    slug="healing-from-emotional-burnout",
                    title_en="Healing from Emotional Burnout: Recognizing Hidden Signs and Reclaiming Rest",
                    title_fa="بهبودی از فرسودگی عاطفی: شناخت نشانه‌های پنهان و بازگشت به تعادل روانی",
                    excerpt_en="Burnout is not just physical tiredness—it is a chronic depletion of emotional reserves. Discover the boundary-setting principles that protect mental wellbeing.",
                    excerpt_fa="فرسودگی صرفاً خستگی جسمی نیست، بلکه خالی شدن تدریجی مخازن عاطفی و احساسی است. اصول تعیین مرزهای سالم برای حفاظت از سلامت روان را بشناسید.",
                    content_en=(
                        "## The Silent Creep of Burnout\n\n"
                        "In our culture of relentless productivity, high achievers often wear chronic exhaustion as a badge of honor. "
                        "Yet true emotional burnout manifests as cynicism, emotional numbness, self-doubt, and persistent apathy.\n\n"
                        "### The Three Dimensions of Burnout\n\n"
                        "- **Exhaustion**: Feeling drained of mental and physical energy even after sleeping.\n"
                        "- **Depersonalization**: Feeling detached from friends, family, or work responsibilities.\n"
                        "- **Reduced Efficacy**: A nagging sense that whatever you do is never quite good enough.\n\n"
                        "### Cultivating Boundary Health\n\n"
                        "Rest is not a reward you earn after collapsing; it is a fundamental biological requirement. Healing requires learning to say no "
                        "without overwhelming guilt and setting compassionate limits around your energy."
                    ),
                    content_fa=(
                        "## نشانه‌های خاموش فرسودگی روانی\n\n"
                        "در دنیایی که مدام ما را به کار و دستاورد بیشتر ترغیب می‌کند، خستگی مزمن اغلب به عنوان فداکاری تلقی می‌شود؛ اما فرسودگی "
                        "عاطفی به شکل بی‌تفاوتی، بدبینی، احساس بی‌کفایتی و کرختی هیجانی بروز می‌کند.\n\n"
                        "### سه بعد اصلی فرسودگی\n\n"
                        "- **فرسودگی شدید**: تخلیه کامل انرژی حتی پس از ساعت‌ها خواب و استراحت.\n"
                        "- **مسخ شخصیت و فاصله عاطفی**: احساس کرختی و دوری نسبت به عزیزان، کار و محیط پیرامون.\n"
                        "- **کاهش کارآمدی ادراک‌شده**: حس پایدار مبنی بر اینکه هر کاری انجام می‌دهید هرگز کافی نیست.\n\n"
                        "### بازتعریف مرزهای شخصی\n\n"
                        "استراحت پاداشی نیست که پس از خرد شدن دریافت کنید؛ بلکه یک ضرورت زیستی حیاتی است. بهبودی با یادگیری «نه گفتن» محترمانه "
                        "بدون احساس عذاب وجدان و اولویت دادن به مراقبت از خود آغاز می‌شود."
                    ),
                    category="Self Care",
                    read_time=5,
                    featured_image="/static/images/article-burnout.svg",
                    published=True
                ),
                Article(
                    slug="communication-in-relationships-moving-from-blame-to-empathy",
                    title_en="Communication in Relationships: Moving from Blame to Empathy",
                    title_fa="ارتباط موثر در روابط عاطفی: گذار از سرزنش به سوی همدلی",
                    excerpt_en="Couples often argue about dishes or schedules when they are actually asking: 'Do you still care about me?' Uncover the emotional subtext behind relationship conflict.",
                    excerpt_fa="زوجین اغلب بر سر کارهای خانه یا برنامه‌ریزی بحث می‌کنند، در حالی که پرسش واقعی زیربنایی این است: «آیا من هنوز برایت مهم هستم؟». رمزگشایی از تعارضات زناشویی را بیاموزید.",
                    content_en=(
                        "## The Subtext of Couple Disagreements\n\n"
                        "Dr. Sue Johnson, pioneer of Emotionally Focused Therapy (EFT), noted that beneath almost every repetitive argument "
                        "lies an attachment cry: 'Are you there for me? Do I matter to you?'\n\n"
                        "When partners feel unheard, they typically adopt one of two protective stances: attacking/criticizing or withdrawing/shutting down. "
                        "This creates an escalating vicious cycle.\n\n"
                        "### Shift from 'You' Statements to Vulnerability\n\n"
                        "Instead of: 'You never listen to me and you are always glued to your phone!'\n\n"
                        "Try expressing the tender primary feeling: 'When you are on your phone during dinner, I feel lonely and miss connecting with you.'"
                    ),
                    content_fa=(
                        "## لایه‌های زیرین تعارضات زوجین\n\n"
                        "پژوهش‌های حوزه زوج‌درمانی هیجان‌مدار (EFT) نشان می‌دهد که در پس اکثر مشاجرات تکراری، یک فریاد دلبستگی نهفته است: "
                        "«آیا من برای تو اهمیت دارم؟ آیا در روزهای سخت کنارم هستی؟»\n\n"
                        "هنگامی که احساس ناامنی رخنه می‌کند، یکی از طرفین معمولاً به انتقاد و حمله روی می‌آورد و دیگری به سکوت و عقب‌نشینی. "
                        "این چرخه فرساینده هر دو را خسته می‌کند.\n\n"
                        "### تبدیل پیام‌های سرزنشگرانه به ابراز نیاز اصیل\n\n"
                        "به جای: «تو هیچ‌وقت به من گوش نمیدی و همش سرت تو گوشیه!»\n\n"
                        "بیان احساس آسیب‌پذیر اصلی: «وقتی موقع شام سرگرم تلفن همراه هستی، احساس تنهایی می‌کنم و دلم برای صحبت صمیمانه با تو تنگ می‌شود»."
                    ),
                    category="Relationships",
                    read_time=7,
                    featured_image="/static/images/article-relationships.svg",
                    published=True
                ),
                Article(
                    slug="mindfulness-for-busy-minds",
                    title_en="Mindfulness for Busy Minds: Practical Everyday Micro-Practices",
                    title_fa="ذهن‌آگاهی برای ذهن‌های پرمشغله: تمرین‌های کوچک و کاربردی روزمره",
                    excerpt_en="You do not need to sit in silence for hours on a mountaintop. Mindfulness is about weaving mindful awareness into ordinary daily moments.",
                    excerpt_fa="ذهن‌آگاهی نیازمند ساعت‌ها نشستن در سکوت کوهستان نیست؛ بلکه هنر آوردن توجه آگاهانه و مهربانانه به لحظه‌های ساده زندگی روزمره است.",
                    content_en=(
                        "## Demystifying Mindfulness\n\n"
                        "Many clients tell me: 'Dr. Fathi, I cannot meditate; my brain simply never stops thinking.'\n\n"
                        "Good news: mindfulness is not about emptying your mind. The mind thinks just as the heart beats. "
                        "Mindfulness is simply noticing that you are thinking, without chasing or battling the thoughts.\n\n"
                        "### Three 60-Second Micro-Practices\n\n"
                        "1. **Mindful Morning Sip**: Feel the warmth of your morning tea or coffee in your hands before taking the first sip.\n"
                        "2. **The Doorway Breath**: Every time you walk through a doorway into another room, take one deep, grounding conscious breath.\n"
                        "3. **Physical Sensations Check-in**: Drop your shoulders away from your ears, unclench your jaw, and let your belly soften."
                    ),
                    content_fa=(
                        "## رهایی از سوءتعبیرها درباره ذهن‌آگاهی\n\n"
                        "بسیاری از مراجعین می‌گویند: «من نمی‌توانم مدیتیشن کنم، چون افکارم یک لحظه هم متوقف نمی‌شوند.»\n\n"
                        "خبر خوب این است که هدف ما خاموش کردن افکار نیست. کار مغز فکر کردن است، همان‌طور که کار قلب تپیدن است. "
                        "ذهن‌آگاهی یعنی متوجه شدن حضور افکار بدون درگیر شدن یا قضاوت کردن آن‌ها.\n\n"
                        "### سه تمرین ۶۰ ثانیه‌ای برای زندگی روزمره\n\n"
                        "۱. **نوشیدن آگاهانه چای یا قهوه**: قبل از اولین جرعه، گرمای فنجان و عطر آن را با تمام وجود حس کنید.\n"
                        "۲. **تنفس پشت چارچوب در**: هر بار که از درِ اتاقی عبور می‌کنید، یک نفس عمیق و آگاهانه بکشید.\n"
                        "۳. **وارسی وضعیت بدنی**: شانه‌های خود را پایین بیندازید، عضلات فک را آزاد کنید و اجازه دهید شکم در آرامش قرار گیرد."
                    ),
                    category="Mindfulness",
                    read_time=4,
                    featured_image="/static/images/article-mindfulness.svg",
                    published=True
                )
            ]
            for art in articles:
                db.add(art)
            print("Seeded 4 comprehensive bilingual articles")

        # 4. Initial Sample Appointments for Admin view
        if db.query(AppointmentRequest).count() == 0:
            sample_requests = [
                AppointmentRequest(
                    client_name="Sarah Jenkins",
                    email="sarah.j@example.com",
                    phone="+1 (555) 234-5678",
                    preferred_date="2026-11-15",
                    preferred_time="Morning (9:00 - 12:00)",
                    service_type="Anxiety & Stress Management",
                    session_format="Online",
                    notes="Struggling with severe work burnout and panic symptoms when presenting in meetings.",
                    status="Pending",
                    language_used="en"
                ),
                AppointmentRequest(
                    client_name="محمد رضایی",
                    email="m.rezaei@example.com",
                    phone="09121112233",
                    preferred_date="1405/08/25",
                    preferred_time="عصر (۱۳:۰۰ تا ۱۷:۰۰)",
                    service_type="زوج‌درمانی و بهبود روابط عاطفی",
                    session_format="In-Person",
                    notes="برای بهبود الگوهای ارتباطی و رفع سوءتفاهم‌های مداوم با همسرم درخواست وقت مشاوره دارم.",
                    status="Confirmed",
                    therapist_notes="جلسه ارزیابی اولیه هماهنگ شد - پنجشنبه ساعت ۱۴:۳۰",
                    language_used="fa"
                ),
                AppointmentRequest(
                    client_name="Elena Rostova",
                    email="elena.r@example.org",
                    phone="+44 20 7946 0912",
                    preferred_date="2026-11-18",
                    preferred_time="Evening (17:00 - 20:00)",
                    service_type="Life Transitions & Identity",
                    session_format="Online",
                    notes="Recently relocated for career and finding it difficult to adapt and manage social isolation.",
                    status="Pending",
                    language_used="en"
                )
            ]
            for req in sample_requests:
                db.add(req)
            print("Seeded initial appointment requests for Admin Portal")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
