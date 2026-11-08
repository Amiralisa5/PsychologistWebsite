import datetime
import json
from app.database import Base, engine, SessionLocal
from app.models import AdminUser, TherapistProfile, AppointmentRequest, Article, SocialSettings, ClinicEvent
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

        # 1.5 Social Settings
        social = db.query(SocialSettings).first()
        if not social:
            social = SocialSettings(
                telegram_enabled=True,
                telegram_bot_token="",
                telegram_channel_id="@dasein_journal",
                telegram_auto_publish=True,
                instagram_enabled=True,
                instagram_account_id="",
                instagram_access_token="",
                instagram_page_handle="dasein.journal",
                instagram_auto_publish=False
            )
            db.add(social)
            print("Created default SocialSettings record")

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

        # 3. Authentic Articles by Dr. Hassan Agha Nasiri (Dasein Journal)
        # Clear existing or ensure authentic ones exist
        db.query(Article).delete()
        articles = [
            Article(
                slug="individual-migration-collective-trauma",
                title_en="Individual Migration, Collective Trauma: The Unspoken Psychological Architecture of Displacement",
                title_fa="مهاجرت یک نفره، ترومای دسته‌جمعی: واکاوی ابعاد روان‌شناختی مهاجرت و غربت",
                excerpt_en="Migration is often celebrated as an individual victory, but beneath lies an existential rupture—an ambiguous loss that echoes across families, relationships, and identity.",
                excerpt_fa="مهاجرت اغلب به عنوان یک دستاورد فردی نگریسته می‌شود، اما در لایه‌های پنهان روان، با گسستی اگزیستانسیال و سوگی مبهم همراه است که تمام پیوندهای عاطفی و هویتی را دگرگون می‌سازد.",
                content_en=(
                    "## The Mirage of Solitary Departure\n\n"
                    "When a person packs their life into two suitcases and crosses borders, society tends to view the event through the lens of individual triumph or career advancement. "
                    "However, in existential clinical psychotherapy, we observe that no migration is ever truly solitary.\n\n"
                    "Every migrant carries the phantom weight of those left behind. In psychoanalytic terms, this creates an **ambiguous loss**—a state of mourning without a funeral, where the homeland remains alive yet out of reach.\n\n"
                    "### The Split Self: Living in Two Time Zones\n\n"
                    "Migrants frequently describe a pervasive sensation of psychological dissonance:\n"
                    "- **Temporal Bifurcation**: The body resides in London, Berlin, or Toronto, but the autonomic nervous system remains tethered to Tehran.\n"
                    "- **Survivor's Guilt**: An ongoing, low-grade guilt whenever enjoying stability, safety, or rest, knowing loved ones back home face instability.\n"
                    "- **Loss of Relational Mirroring**: The loss of subtle cultural nuances, shared humor, and the comfort of speaking in one's mother tongue without translation filters.\n\n"
                    "### The Therapeutic Path: From Fragmentation to Integration\n\n"
                    "Healing does not require severing roots or forcing immediate assimilation. Rather, therapy provides a secure holding environment to honor the grief, reconcile the dual identities, and reconstruct an integrated, authentic sense of Being-in-the-world (Dasein)."
                ),
                content_fa=(
                    "## توهم مهاجرت فردی\n\n"
                    "هنگامی که فردی تمام زندگی‌اش را در دو چمدان خلاصه می‌کند و از مرزها می‌گذرد، جامعه اغلب به آن به چشم یک پیروزی فردی یا فرصت شغلی نگاه می‌کند. "
                    "اما در اتاق روان‌درمانی اگزیستانسیال، ما می‌بینیم که هیچ مهاجرتی هرگز «یک‌نفره» رخ نمی‌دهد.\n\n"
                    "هر فرد مهاجر، بار روانی ناپیدای خانواده، ریشه‌ها و خاطراتی را که جا گذاشته با خود حمل می‌کند. این تجربه در روانشناسی «سوگ مبهم» (Ambiguous Loss) نامیده می‌شود؛ فقدانی بدون سنگ قبر، که در آن وطن همچنان وجود دارد اما دسترس‌پذیر نیست.\n\n"
                    "### روان دوشقه: زیستن همزمان در دو افق زمانی\n\n"
                    "مهاجران معمولاً با نشانه‌های عمیقی از تعارض روانی دست و پنجه نرم می‌کنند:\n"
                    "۱. **تفرقه زمانی و حسی**: جسم در تورنتو، برلین یا لندن قدم می‌زند، اما سیستم عصبی و دلواپسی‌ها همچنان در کوچه‌های تهران سیر می‌کند.\n"
                    "۲. **عذاب وجدان بازمانده (Survivor's Guilt)**: حس مداوم شرم یا گناه در لحظاتی که فرد به امنیت یا آرامش نسبی می‌رسد، در حالی که عزیزانش با چالش‌های وطن روبرو هستند.\n"
                    "۳. **فقدان زبان مادری و بازتاب هیجانی**: غربت زبان، عدم درک شوخی‌ها و ظرافت‌های فرهنگی، و انزوای تدریجی در ارتباطات جدید.\n\n"
                    "### مسیر التیام در روان‌درمانی\n\n"
                    "بهبودی به معنای بریدن از ریشه‌ها یا هضم تحمیلی در فرهنگ مقصد نیست. هدف روان‌درمانی اگزیستانسیال، به رسمیت شناختن این سوگ، بازسازی پیوند با خود واقعی و دستیابی به هویتی یکپارچه و اصیل در «اینجا و اکنون» (Dasein) است."
                ),
                category="Life Transitions & Identity",
                read_time=7,
                featured_image="/static/images/article-burnout.svg",
                published=True
            ),
            Article(
                slug="trauma-beyond-invisible-scars-ptsd",
                title_en="Trauma: Beyond Invisible Scars — How the Body Keeps the Score and How Psychotherapy Heals",
                title_fa="تروما فراتر از زخم‌های نادیدنی: بررسی اختلال استرس پس از سانحه (PTSD) و راه‌های بهبودی",
                excerpt_en="Trauma is not merely what happened to you in the past; it is the imprint that experience leaves on your nervous system, reshaping your sense of safety, memory, and presence.",
                excerpt_fa="تروما صرفاً یک خاطره تلخ در گذشته نیست؛ بلکه اثر ماندگاری است که واقعه بر سیستم عصبی و ساختار باورهای فرد بر جای می‌گذارد و احساس امنیت در زمان حال را سلب می‌کند.",
                content_en=(
                    "## Deconstructing Trauma\n\n"
                    "We often assume trauma only belongs to extreme war zones or cataclysmic catastrophes. Yet developmental trauma, emotional neglect, betrayal, or chronic relational stress can leave scars just as severe.\n\n"
                    "Trauma occurs whenever an overwhelming experience exceeds the nervous system's capacity to process and integrate it.\n\n"
                    "### The Neurobiology of Flashbacks and Hypervigilance\n\n"
                    "In PTSD and complex trauma, the prefrontal cortex goes offline while the amygdala stays stuck in overdrive. Time collapses: a current sound, tone of voice, or scent triggers the exact physiological dread of the original event.\n\n"
                    "### Integrated Clinical Approaches\n\n"
                    "1. **Somatic Grounding**: Restoring bodily safety before intellectual exploration.\n"
                    "2. **EMDR & Bilateral Stimulation**: Reprocessing traumatic fragments so they become integrated past memories rather than active threats.\n"
                    "3. **Existential Meaning Rebuilding**: Reclaiming agency and constructing a life defined by self-worth, not by victimization."
                ),
                content_fa=(
                    "## بازشناسی مفهوم واقعی تروما\n\n"
                    "بسیاری گمان می‌کنند تروما تنها مختص حوادث مرگبار یا جنگ‌های ویرانگر است. اما ترومای رشدی، نادیده‌گرفته‌شدن در کودکی، خیانت‌های عاطفی و فشارهای روانی مزمن می‌توانند همان اندازه سیستم روانی فرد را از هم بپاشند.\n\n"
                    "تروما زمانی رخ می‌دهد که شدت یک تجربه دردناک از ظرفیت پردازش و تاب‌آوری سیستم عصبی فراتر می‌رود.\n\n"
                    "### فیزیولوژی کابوس‌ها و گوش‌به‌زنگی مداوم\n\n"
                    "در اختلال استرس پس از سانحه (PTSD)، مغز منطقی به حاشیه رانده شده و مرکز هشدار (آمیگدال) در وضعیت آماده‌باش قرمز باقی می‌ماند. زمان در هم می‌شکند: یک بوی خاص، تغییر لحن صدا یا تنشی ساده در محیط کار، تمام هراس واقعه اولیه را در ثانیه‌ای زنده می‌کند.\n\n"
                    "### راهکارهای درمانی در کلینیک دازاین\n\n"
                    "۱. **تثبیت حسی و آرام‌سازی جسمانی**: بازگرداندن حس امنیت بنیادین به تن پیش از واکاوی ذهنی.\n"
                    "۲. **پردازش تروما و EMDR**: تبدیل تکه‌های پراکنده و منجمد خاطره به رویدادهایی که «به گذشته تعلق دارند» و تهدید اکنون نیستند.\n"
                    "۳. **بازسازی معنای وجودی**: بازپس‌گیری عاملیت زندگی و زیستن بر مبنای ارزش‌های اصیل، نه بر پایه دفاع‌های آسیب‌زده."
                ),
                category="Trauma & Healing",
                read_time=6,
                featured_image="/static/images/article-anxiety.svg",
                published=True
            ),
            Article(
                slug="hide-your-defilement-psychoanalysis-superego-shame",
                title_en="Hide Your Defilement: Psychoanalysis, the Tyranny of the Superego, and Chronic Shame",
                title_fa="«نجاستت را پنهان کن!»: با نگاهی به روانکاوی، سوپرایگو، عقده شرم و بازداری‌های روانی",
                excerpt_en="From early childhood taboos to adult neurosis, the internal judge (Superego) demands relentless purification. Explore how unconscious shame stifles instinct and vitality.",
                excerpt_fa="از تابوهای دوران کودکی تا وسواس‌های بزرگسالی، قاضی سرزنشگر درونی مدام بر پنهان‌سازی و تطهیر اصرار دارد. واکاوی مکانیزم‌های دفاعی و عقده شرم در روانکاوی فرویدی.",
                content_en=(
                    "## The Birth of the Punitive Superego\n\n"
                    "Sigmund Freud demonstrated that our most debilitating adult anxieties do not originate from external oppressors, but from an internalized inquisitor—the **Superego**.\n\n"
                    "From our earliest bodily training, human cultures whisper: 'Conceal your bodily functions, hide your desires, conceal your flaws.' Over time, this natural socialization can metastasize into pathological shame.\n\n"
                    "### Shame vs. Guilt\n\n"
                    "- **Guilt**: 'I did something mistakes.' (Focus on behavior)\n"
                    "- **Shame**: 'I am fundamentally flawed, soiled, and unlovable.' (Focus on Being)\n\n"
                    "In our clinical work, dismantling this tyrannical inner critic is central to freeing the individual's creative vitality."
                ),
                content_fa=(
                    "## پیدایش سوپرایگوی تنبیه‌گر\n\n"
                    "زیگموند فروید نشان داد که عمیق‌ترین اضطراب‌ها و وسواس‌های بزرگسالی نه از دشمنان بیرونی، بلکه از یک قاضی درونی‌شده به نام «سوپرایگو» یا فراخود سرچشمه می‌گیرند.\n\n"
                    "از نخستین آموزش‌های تربیتی دوران کودکی، این پیام در ناخودآگاه کاشته می‌شود: «ناپاکی‌ات را پنهان کن، غرایزت را سرکوب کن، نقص‌هایت را بپوشان». با گذشت زمان، این آموزه‌ها به یک شرم مزمن و فلج‌کننده وجودی بدل می‌شوند.\n\n"
                    "### تمایز بنیادین گناه و شرم\n\n"
                    "- **احساس گناه**: «من کار اشتباهی انجام دادم» (تمرکز بر رفتار که قابل جبران است).\n"
                    "- **احساس شرم عمیق**: «من اساساً کثیف، ناکافی و دوست‌نداشتنی هستم» (تمرکز بر هستی فرد که به انزوا و خودتخریبی می‌انجامد).\n\n"
                    "در جلسات روان‌درمانی تحلیلی، ما ریشه‌های این قضاوت‌های بیرحمانه را کالبدشکافی می‌کنیم تا انرژی روانی که صرف خودپنهان‌سازی شده، به سرزندگی، اصالت و خلاقیت تبدیل گردد."
                ),
                category="Psychoanalysis & Mind",
                read_time=8,
                featured_image="/static/images/article-relationships.svg",
                published=True
            ),
            Article(
                slug="the-heart-operated-the-mind-frozen-in-surgery",
                title_en="The Heart Was Operated On, But the Mind Remains in Surgery: Psychosomatics and Health Anxiety",
                title_fa="«قلبی که جراحی شد، اما ذهن هنوز در اتاق عمل است!»: روان‌تنی، اضطراب بیماری و ارتباط ذهن و بدن",
                excerpt_en="Physical healing on an operating table does not guarantee psychic recovery. Why does medical trauma persist in the autonomic nervous system long after the incision has healed?",
                excerpt_fa="ترمیم جسم بر روی تخت جراحی، به معنای التیام روان نیست. چرا ترومای بیماری و بیهوشی در سیستم عصبی خودمختار باقی می‌ماند و چگونه به روان‌درمانی پاسخ می‌دهد؟",
                content_en=(
                    "## The Cartesian Illusion\n\n"
                    "Modern medicine has performed miracles by treating the physical body as an intricate biological machine. Yet cardiologists, surgeons, and physicians often encounter a puzzling phenomenon: "
                    "the patient's lab results are flawless, the ECG is normal, yet the patient feels terrified, breathless, and convinced they are dying.\n\n"
                    "### Somatization of Dread\n\n"
                    "The mind and body are an indivisible continuum. When a medical crisis threatens our mortality, the brain experiences an existential shock. The surgical environment—loss of control under anesthesia, needles, alarms—is perceived by the nervous system as an existential assault.\n\n"
                    "### Re-inhabiting the Body\n\n"
                    "Psychotherapy bridges the chasm between medical restoration and psychological peace, enabling clients to trust their heartbeat once more."
                ),
                content_fa=(
                    "## خطای تفکیک ذهن و جسم\n\n"
                    "پزشکی مدرن دستاوردهای شگرفی در نجات جان انسان‌ها داشته است، اما جراحان و متخصصان قلب مکرراً با بیمارانی روبرو می‌شوند که تمام آزمایش‌ها و اکوهای قلبی‌شان کاملاً نرمال است، ولی همچنان با تپش قلب شدید، وحشت مرگ و احساس تنگی نفس به اورژانس بازمی‌گردند.\n\n"
                    "### روان‌تنی و وحشت منجمدشده\n\n"
                    "ذهن و تن، کلیتی یگانه هستند. هنگامی که یک بحران جسمانی مرگ‌آگاهی را بیدار می‌کند، اتاق عمل، صداهای آلارم مانیتورها و احساس ناتوانی محض زیر بیهوشی، شوکی اگزیستانسیال ایجاد می‌کند که سال‌ها بعد می‌تواند در قالب حملات پانیک یا اضطراب سلامتی بازتولید شود.\n\n"
                    "### بازگشت اعتماد به طپش‌های زندگی\n\n"
                    "در رویکرد روان‌درمانی یکپارچه‌نگر، به مراجع کمک می‌شود تا پیام‌های اضطراب را از خطرات واقعی تفکیک کند و رابطه‌ای آشتی‌جویانه و امن با جسم خویش برقرار سازد."
                ),
                category="Psychosomatics",
                read_time=6,
                featured_image="/static/images/article-mindfulness.svg",
                published=True
            ),
            Article(
                slug="self-harm-and-injury-among-youth",
                title_en="Self-Harm and Injury Among Youth: Decoding Non-Suicidal Self-Injury as a Language of Pain",
                title_fa="رفتارهای خودآسیب‌رسان و خودزنی در میان جوانان: رمزگشایی از رنج هیجانی و راه‌های مداخله تخصصی",
                excerpt_en="Self-injury is not attention-seeking—it is a desperate somatic coping mechanism to regulate unbearable psychic agony. An evidence-based guide for families and educators.",
                excerpt_fa="خودزنی جلب توجه نیست؛ بلکه تلاش درمانده جسمانی برای تنظیم درد هیجانی غیرقابل‌تحمل است. راهنمای بالینی و همدلانه برای خانواده‌ها و نسل جوان.",
                content_en=(
                    "## Non-Suicidal Self-Injury (NSSI)\n\n"
                    "When psychological anguish reaches a breaking point and words fail, the body becomes the canvas for the unsaid.\n\n"
                    "### Why Do Individuals Self-Harm?\n\n"
                    "- **Affect Regulation**: Physical pain stimulates endorphin release, providing temporary numbness from emotional turmoil.\n"
                    "- **Anti-Dissociation**: Feeling tangible physical sensation to escape deep numbness or detachment.\n"
                    "- **Self-Punishment**: Enacting internalized blame and feelings of unworthiness.\n\n"
                    "### Compassionate Interventions\n\n"
                    "Shaming or confiscating objects rarely solves the core distress. Dialectical Behavior Therapy (DBT), somatic grounding, and existential validation offer real alternatives to heal the underlying wound."
                ),
                content_fa=(
                    "## درک رفتارهای خودآسیب‌رسان غیرخودکشی (NSSI)\n\n"
                    "هنگامی که درد و غلیان هیجانی به نقطه‌ای غیرقابل تحمل می‌رسد و واژگان برای ابراز رنج کافی نیستند، جسم به بستری برای بیان ناگفته‌ها بدل می‌شود.\n\n"
                    "### چرا افراد به خودآسیب‌رسانی روی می‌آورند؟\n\n"
                    "۱. **تنظیم و تسکین هیجانی**: درد فیزیکی با ترشح اندورفین، کرختی موقتی در برابر طوفان هیجانات ایجاد می‌کند.\n"
                    "۲. **فرار از گسست و کرختی روانی (Anti-Dissociation)**: حس کردن دردی ملموس برای اطمینان از زنده بودن در دوران بی‌رمقی احساسی.\n"
                    "۳. **سرزنش و خودتنبیهی ناهشیار**: تخلیه خشم درونی‌شده ناشی از احساس بی‌ارزشی.\n\n"
                    "### رویکرد همدلانه و تخصصی در درمان\n\n"
                    "سرزنش، تحقیر یا تهدید هرگز گره‌گشا نیست. درمان رفتارشناختی دیالکتیکی (DBT)، مهارت‌های تحمل پریشانی و فضایی امن در روان‌درمانی به جوانان می‌آموزد که چگونه بدون آسیب به خود، هیجانات سنگین را مدیریت کنند."
                ),
                category="Youth & Emotional Health",
                read_time=7,
                featured_image="/static/images/article-default.svg",
                published=True
            ),
            Article(
                slug="psychology-and-tarikh-e-beyhaqi-classical-literature",
                title_en="Psychological Analysis of Classical Persian Literature: Psychology & Tarikh-e Beyhaqi",
                title_fa="بررسی آثار ادبیات کلاسیک فارسی بر اساس نظریات روان‌شناسی: مجموعه‌ی «روان‌شناسی و تاریخ بیهقی»",
                excerpt_en="A psychological inquiry into the characters, anxiety typologies, and defense mechanisms in classical Persian literature through the lens of Tarikh-e Beyhaqi.",
                excerpt_fa="تحلیل و بررسی عمیق ساختار روانی، لایه‌های شخصیتی، گونه‌شناسی اضطراب و مکانیسم‌های دفاعی در تاریخ بیهقی از منظر مکاتب نوین روان‌شناسی و روانکاوی.",
                content_en=(
                    "## Classical Literature Through a Psychological Lens\n\n"
                    "Published as part of the **Dasein Journal** research series (Instagram [@dasein.journal](https://instagram.com/dasein.journal) & Telegram [@dasein_journal](https://t.me/dasein_journal)), "
                    "this study explores how ancient historical narratives reflect eternal structures of the human psyche.\n\n"
                    "Abu'l-Fadl Bayhaqi's masterpiece is not merely a chronicle of Ghaznavid court intrigues; it is an extraordinary psychological document illustrating power neurosis, narcissistic vulnerability, and existential terror.\n\n"
                    "### Core Analytical Themes\n\n"
                    "1. **Typology of Anxiety & Defense Mechanisms**: Analyzing how historical figures used projection, reaction formation, and denial to manage political and existential dread.\n"
                    "2. **Psycholinguistics of Bayhaqi's Prose**: How deliberate syntactic rhythms and word choices mirror emotional suppression and psychological tension.\n"
                    "3. **Neo-Freudian Personality Characterization**: Exploring the relational complexes and narcissistic wounds of rulers and ministers.\n"
                    "4. **Kohlberg's Stages of Moral Development**: Mapping the ethical dilemmas and moral development stages of pivotal historical figures.\n\n"
                    "### 📎 Scientific Research Papers & Sources (Available on Telegram Channel)\n\n"
                    "- [**گونه‌شناسی اضطراب و مکانیسم‌های دفاعی (PDF)**](https://t.me/dasein_journal/14) — 1.5 MB\n"
                    "- [**روانشناسی زبان تاریخ بیهقی (PDF)**](https://t.me/dasein_journal/15) — 1.4 MB\n"
                    "- [**نقد روانکاوانه شخصیت‌ها بر اساس مکتب نوفرویدی (PDF)**](https://t.me/dasein_journal/16) — 451 KB\n"
                    "- [**بررسی تاریخ بیهقی بر اساس نظریه رشد اخلاقی کلبرگ (PDF)**](https://t.me/dasein_journal/17) — 1.3 MB\n"
                    "- [**روانشناسی در تاریخ بیهقی — رساله جامع (PDF)**](https://t.me/dasein_journal/18) — 5.5 MB\n"
                ),
                content_fa=(
                    "## بازخوانی ادبیات کهن با نگاه روان‌شناختی\n\n"
                    "این مقاله برگرفته از مجموعه پژوهشی اختصاصی **ژورنال دازاین** (منتشرشده در اینستاگرام [@dasein.journal](https://instagram.com/dasein.journal) و تلگرام [@dasein_journal](https://t.me/dasein_journal)) است که به تحلیل پیوند ادبیات کلاسیک و ساختارهای روانی انسان می‌پردازد.\n\n"
                    "شاهکار ابوالفضل بیهقی صرفاً تاریخ‌نگاری وقایع دربار غزنوی نیست؛ بلکه بستری کم‌نظیر برای کالبدشکافی تعارضات درونی، عقده‌های روانی، و تجلی «اضطراب مرگ و قدرت» در بستر مناسبات انسانی است.\n\n"
                    "### محورهای تحلیلی مجموعه\n\n"
                    "۱. **گونه‌شناسی اضطراب و مکانیسم‌های دفاعی**: بررسی نحوه واکنش دولتمردان و وزرا به تهدیدهای محیطی از طریق برون‌فکنی، واپس‌رانی و واکنش وارونه.\n"
                    "۲. **روان‌شناسی زبان نثر بیهقی**: چگونه سکوت‌ها، مکث‌ها و ایجاز زبان بیهقی، حامل سرکوب‌های هیجانی راوی و اضطراب محیط است.\n"
                    "۳. **نقد روانکاوانه بر پایه مکاتب نوفرویدی**: تحلیل نیازهای روان‌رنجورانه به قدرت و تأیید، و آسیب‌پذیری‌های خودشیفتگی در چهره‌های تاریخی.\n"
                    "۴. **سنجش مراحل رشد اخلاقی کلبرگ**: تحلیل دوراهی‌های اخلاقی و مرز میان مصلحت‌سنجی ترسو و شجاعت اخلاقی اصیل.\n\n"
                    "### 📎 مقالات علمی و منابع پژوهشی کامل (قابل دریافت از کانال تلگرام دازاین)\n\n"
                    "- [**گونه‌شناسی اضطراب و مکانیسم‌های دفاعی (PDF)**](https://t.me/dasein_journal/14) — حجم: ۱.۵ مگابایت\n"
                    "- [**روانشناسی زبان تاریخ بیهقی (PDF)**](https://t.me/dasein_journal/15) — حجم: ۱.۴ مگابایت\n"
                    "- [**نقد روانکاوانه شخصیت‌ها بر اساس مکتب نوفرویدی (PDF)**](https://t.me/dasein_journal/16) — حجم: ۴۵۱ کیلوبایت\n"
                    "- [**بررسی تاریخ بیهقی بر اساس نظریه رشد اخلاقی کلبرگ (PDF)**](https://t.me/dasein_journal/17) — حجم: ۱.۳ مگابایت\n"
                    "- [**روانشناسی در تاریخ بیهقی — رساله جامع (PDF)**](https://t.me/dasein_journal/18) — حجم: ۵.۵ مگابایت\n"
                ),
                category="Literature & Psychoanalysis",
                read_time=10,
                featured_image="/static/images/article-beyhaqi.svg",
                published=True,
                telegram_posted=True,
                telegram_post_id="3",
                instagram_posted=True,
                instagram_post_id="carousel_1"
            ),
            Article(
                slug="grief-soog-psychology-philosophy-iranian-rituals",
                title_en="Grief (Soog): Perspectives from Psychology, Philosophy, and Iranian Cultural Rituals",
                title_fa="«سوگ» از دیدگاه روان، فلسفه، آیین و رسوم ایرانی",
                excerpt_en="Dissecting grief and bereavement: psychological mourning processes, cultural rituals, archetypes in Ferdowsi's Shahnameh, and existential integration.",
                excerpt_fa="کالبدشکافی پدیده سوگ و ماتم، فرآیند التیام روانی، کهن‌الگوهای اندوه در شاهنامه فردوسی و مقایسه آیین‌های سوگواری سنتی با نظریات اگزیستانسیال.",
                content_en=(
                    "## The Universality and Cultural Specificity of Grief\n\n"
                    "Published as part of the **Dasein Journal** publication series on Instagram ([@dasein.journal](https://instagram.com/dasein.journal)) and Telegram ([@dasein_journal](https://t.me/dasein_journal)).\n\n"
                    "Grief is one of the most fundamental existential givens. While modern psychiatry often medicalizes bereavement into depressive syndromes, Iranian philosophical and literary traditions have long understood mourning as an active, sacred psychological passage.\n\n"
                    "### The Mourning Archetypes in Shahnameh\n\n"
                    "In Ferdowsi's Shahnameh (such as the tragedy of Sohrab or Siavash), mourning is not a passive surrender; it is a ritualized communal catharsis that allows the collective psyche to endure the unbearable weight of mortality.\n\n"
                    "### Integrating Grief in Existential Therapy\n\n"
                    "- **Moving past 'closure'**: Acceptance does not mean forgetting; it means integrating the loss into one's enduring narrative.\n"
                    "- **The role of cultural ritual**: Why communal gathering and somatic expressions of sorrow protect against complicated, disenfranchised grief.\n\n"
                    "### 📎 Scientific Research Paper (Available on Telegram)\n\n"
                    "- [**تحلیل ساختاری سوگ با سوگ‌نگاره شاهنامه (PDF)**](https://t.me/dasein_journal/22) — 1.1 MB\n"
                ),
                content_fa=(
                    "## جهان‌شمولی و هویت فرهنگی سوگ\n\n"
                    "این مقاله بازتابی از پژوهش منتشرشده در **ژورنال دازاین** (اینستاگرام [@dasein.journal](https://instagram.com/dasein.journal) و تلگرام [@dasein_journal](https://t.me/dasein_journal)) است.\n\n"
                    "سوگ (Mourning) رویارویی ناگزیر انسان با یکی از چهار دلواپسی غایی وجودی یعنی «مرگ و فقدان» است. در حالی که روانپزشکی غرب گاه سوگ را به نشانه‌های افسردگی فرو می‌کاهد، سنت فرهنگی، فلسفی و اسطوره‌ای ایران سوگ را یک «گذار روانی مقدس» و پیوندی عمیق میان فرد و جامعه می‌داند.\n\n"
                    "### سوگ‌نگاره‌های شاهنامه و کهن‌الگوهای روانی\n\n"
                    "در سوگ‌سروده‌های شاهنامه فردوسی (نظیر سوگ سیاوش و سهراب)، سوگواری تنها یک واکنش انفعالی نیست؛ بلکه آیینی جمعی برای تخلیه بار هیجانی، معنابخشی مجدد به رنج، و پیشگیری از فرورفتن فرد در انزوای مالیخولیا (Melancholia) است.\n\n"
                    "### التیام سوگ در روان‌درمانی اگزیستانسیال\n\n"
                    "۱. **فراتر از توهم «فراموشی»**: درمان سوگ فراموش کردن عزیز از دست رفته نیست، بلکه بازآفرینی رابطه درونی با او و گنجاندن فقدان در تاروپود هویت جدید است.\n"
                    "۲. **کارکرد آیین‌ها**: چگونه رسوم سوگواری اصیل ایرانی از تبدیل شدن سوگ طبیعی به سوگ بیمارگون و یخ‌زده محافظت می‌کنند.\n\n"
                    "### 📎 مقاله علمی و پژوهشی کامل (قابل دریافت از کانال تلگرام دازاین)\n\n"
                    "- [**تحلیل ساختاری سوگ با سوگ‌نگاره شاهنامه (PDF)**](https://t.me/dasein_journal/22) — حجم: ۱.۱ مگابایت\n"
                ),
                category="Grief & Existential Loss",
                read_time=8,
                featured_image="/static/images/article-grief.svg",
                published=True,
                telegram_posted=True,
                telegram_post_id="19",
                instagram_posted=True,
                instagram_post_id="carousel_2"
            )
        ]
        for art in articles:
            db.add(art)
        print("Seeded 7 authentic articles from Dr. Hassan Agha Nasiri / Dasein Journal")

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

        # 5. Clinic Events / Upcoming Webinars
        if db.query(ClinicEvent).count() == 0:
            webinar = ClinicEvent(
                title_en="Specialized Clinical Webinar: Grief, Trauma & Defense Mechanisms in Classical Literature",
                title_fa="کارگاه آنلاین و تخصصی: سوگ، تروما و مکانیزم‌های دفاع روانی در شاهنامه و تاریخ بیهقی",
                description_en="Join Dr. Hassan Agha Nasiri for an in-depth clinical and existential exploration of mourning, ambiguous loss, and coping mechanisms.",
                description_fa="وبینار تخصصی تحلیل کهن‌الگوهای سوگ، تروما و مکانیزم‌های دفاعی با حضور دکتر حسن آقانصیری. بررسی پیوند متون کهن با التیام روان‌شناختی معاصر.",
                event_date="2026-11-20",
                event_time="18:00 - 20:00 (Tehran Time)",
                event_format="Online (Google Meet)",
                meet_link="https://meet.google.com/das-ein-meet",
                location_en="Online via Google Meet",
                location_fa="آنلاین از طریق گوگل میت (Google Meet)",
                is_active=True
            )
            db.add(webinar)
            print("Seeded initial ClinicEvent")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
