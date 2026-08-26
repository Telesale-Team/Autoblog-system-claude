"""สร้างโปรไฟล์ 5 มิติของ 6 กลุ่มลูกค้า จากข้อมูลจริงในไฟล์ agent

ข้อมูลทุกบรรทัดในนี้ยกมาจาก `.claude/agents/19-24_*.md` ไม่ได้แต่งขึ้นเอง
ส่วนที่ agent ไม่เคยระบุ (สไตล์ diagram / ท่าปก / สีรอง) เป็นข้อเสนอตั้งต้น
ที่เจ้าของแก้เองได้จากหน้าเว็บ

รันซ้ำได้ ไม่สร้างซ้ำ — ใช้ key เป็นตัวชี้
    manage.py seed_segment_profiles
    manage.py seed_segment_profiles --reset   (เขียนทับค่าที่แก้ไว้แล้ว)
"""

from django.core.management.base import BaseCommand

from marketing.models import SegmentProfile as SP


PROFILES = [
    {
        "key": "healthcare",
        "name": "คลินิก / โรงพยาบาลเอกชน",
        "agent_slug": "healthcare-content-writer",
        "pen_name": "ชบา",
        "pronoun": "หนู / ดิฉัน",
        "tone": "Professional + Trustworthy — เหมือนนิตยสารการแพทย์ ไม่ใช่โฆษณา "
                "อ้างอิงมาตรฐานและกฎหมายเสมอ ไม่เร่งเร้าให้ตัดสินใจ",
        "reader": "ผู้บริหารคลินิก/โรงพยาบาลเอกชน อายุ 35-55 ปี มีการศึกษาสูง "
                  "ให้ความสำคัญกับความน่าเชื่อถือและมาตรฐาน",
        "research": "ประกาศกระทรวงสาธารณสุข\n"
                    "พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล (PDPA)\n"
                    "สถิติสาธารณสุขไทย\n"
                    "กรณีศึกษาโรงพยาบาลที่ใช้ระบบนัดหมายอัตโนมัติ",
        "shape": SP.Shape.SHARP,
        "accent_secondary": "#4A90A4",
        "icon_mood": SP.IconMood.CLEAN,
        "prefer_diagram": SP.DiagramType.COMPARISON,
        "cover_pose": SP.Pose.SERIOUS,
        "cover_mood": SP.Mood.CLEAN,
        "hook_style": "ข้อกำหนดหรือความเสี่ยงที่ผู้บริหารต้องรู้",
    },
    {
        "key": "ecommerce",
        "name": "ร้านค้าออนไลน์ / e-commerce",
        "agent_slug": "ecommerce-content-writer",
        "pen_name": "น้ำตาล",
        "pronoun": "หนู",
        "tone": "Casual + Energetic + FOMO — เหมือนเพื่อนที่ขายของเก่งมาแชร์เคล็ดลับ "
                "ประโยคสั้น กระตุ้นให้ลงมือทันที",
        "reader": "เจ้าของร้านออนไลน์ อายุ 25-40 ปี อยากเพิ่มยอดขาย ลดเวลาตอบแชท "
                  "และแข่งขันกับร้านอื่นได้",
        "research": "รายงานตลาด e-commerce ไทย (ETDA, Priceza)\n"
                    "นโยบายและฟีเจอร์ใหม่ของ Shopee / Lazada / TikTok Shop\n"
                    "สถิติพฤติกรรมผู้ซื้อออนไลน์ไทย\n"
                    "เคสร้านที่โตจากการตอบแชทเร็ว",
        "shape": SP.Shape.ROUNDED,
        "accent_secondary": "#F97316",
        "icon_mood": SP.IconMood.ENERGETIC,
        "prefer_diagram": SP.DiagramType.STATS,
        "cover_pose": SP.Pose.POINTING,
        "cover_mood": SP.Mood.WARM,
        "hook_style": "ตัวเลขยอดขายที่เสียไปถ้าไม่ทำ",
    },
    {
        "key": "hospitality",
        "name": "โรงแรม / รีสอร์ท / ท่องเที่ยว",
        "agent_slug": "hospitality-content-writer",
        "pen_name": "กุ๊กกิ๊ก",
        "pronoun": "หนู",
        "tone": "Aspirational + Professional + Warm — เหมือนนิตยสารท่องเที่ยวระดับ premium "
                "เล่าถึงประสบการณ์แขกก่อนพูดเรื่องระบบ",
        "reader": "เจ้าของ/ผู้จัดการโรงแรมและรีสอร์ท อายุ 35-55 ปี ต้องการเพิ่ม occupancy rate "
                  "และบริหาร OTA ให้มีประสิทธิภาพ",
        "research": "สถิตินักท่องเที่ยว กระทรวงการท่องเที่ยวและกีฬา\n"
                    "ค่าคอมมิชชันและนโยบายของ OTA (Agoda, Booking.com)\n"
                    "รายงาน occupancy rate รายภูมิภาค\n"
                    "รีวิวและพฤติกรรมการจองของนักท่องเที่ยว",
        "shape": SP.Shape.SOFT,
        "accent_secondary": "#0E7490",
        "icon_mood": SP.IconMood.CLEAN,
        "prefer_diagram": SP.DiagramType.CONCEPT,
        "cover_pose": SP.Pose.HAPPY,
        "cover_mood": SP.Mood.WARM,
        "hook_style": "ภาพประสบการณ์แขกที่ดีขึ้นอย่างเป็นรูปธรรม",
    },
    {
        "key": "beauty_wellness",
        "name": "ร้านนวด / สปา / คลินิกความงาม",
        "agent_slug": "beauty-wellness-writer",
        "pen_name": "น้องข้าวเหนียว",
        "pronoun": "หนู",
        "tone": "Warm + Relatable + Encouraging — เหมือนเพื่อนที่เปิดร้านนวดมาแชร์ประสบการณ์ "
                "ภาษาอ่อนโยน เน้นความสัมพันธ์กับลูกค้า",
        "reader": "เจ้าของร้านนวด/สปา อายุ 28-45 ปี ส่วนใหญ่เป็นผู้หญิง ต้องการสร้างลูกค้าประจำ "
                  "เพิ่มการจองออนไลน์ และลดงาน admin",
        "research": "สถิติร้านนวดและสปาขึ้นทะเบียน กรมสนับสนุนบริการสุขภาพ\n"
                    "ขนาดตลาดความงามและสุขภาพไทย\n"
                    "พฤติกรรมการจองคิวผ่าน LINE ของลูกค้าไทย\n"
                    "อัตรา no-show และวิธีลดของร้านจริง",
        "shape": SP.Shape.ROUNDED,
        "accent_secondary": "#E8B4B8",
        "icon_mood": SP.IconMood.SOFT,
        "prefer_diagram": SP.DiagramType.STEPS,
        "cover_pose": SP.Pose.HAPPY,
        "cover_mood": SP.Mood.WARM,
        "hook_style": "คำถามที่เจ้าของร้านเคยเจอกับตัว",
    },
    {
        "key": "hr_education",
        "name": "HR องค์กร / โรงเรียน / สถาบัน",
        "agent_slug": "hr-education-writer",
        "pen_name": "กาแฟ",
        "pronoun": "ผม",
        "tone": "Structured + Data-Driven + Professional — เหมือนบทความใน HR Magazine ไทย "
                "มีหัวข้อย่อยชัด อ้างตัวเลขทุกข้ออ้าง",
        "reader": "HR Manager / ผู้อำนวยการโรงเรียน อายุ 30-50 ปี ต้องการพัฒนาบุคลากร "
                  "ลดงาน admin HR และนำ EdTech มาใช้",
        "research": "รายงานตลาดแรงงานไทย กระทรวงแรงงาน\n"
                    "สถิติการศึกษา กระทรวงศึกษาธิการ\n"
                    "ผลสำรวจ engagement และ turnover ขององค์กรไทย\n"
                    "กฎหมายแรงงานและ PDPA ที่เกี่ยวกับข้อมูลพนักงาน",
        "shape": SP.Shape.SHARP,
        "accent_secondary": "#6366F1",
        "icon_mood": SP.IconMood.TECHNICAL,
        "prefer_diagram": SP.DiagramType.STATS,
        "cover_pose": SP.Pose.READING,
        "cover_mood": SP.Mood.TECH,
        "hook_style": "ตัวเลขต้นทุนที่องค์กรจ่ายอยู่โดยไม่รู้ตัว",
    },
    {
        "key": "creator_coach",
        "name": "โค้ช / อาจารย์ออนไลน์ / creator",
        "agent_slug": "creator-coach-writer",
        "pen_name": "ไมโล",
        "pronoun": "ผม",
        "tone": "Inspirational + Personal + Direct — เหมือนโค้ชที่พูดตรงใจ "
                "มีเรื่องราวส่วนตัวแชร์ ไม่อ้อมค้อม",
        "reader": "โค้ช/ครูออนไลน์ อายุ 25-45 ปี ต้องการสร้าง Personal Brand "
                  "สร้างรายได้ออนไลน์ และใช้ AI ช่วยทำ content",
        "research": "สถิติ creator economy ไทย\n"
                    "ค่าคอมมิชชันและกติกาของแพลตฟอร์มคอร์สออนไลน์\n"
                    "พฤติกรรมผู้เรียนออนไลน์ไทย\n"
                    "เคสโค้ชที่สร้างรายได้จาก personal brand",
        "shape": SP.Shape.ROUNDED,
        "accent_secondary": "#A855F7",
        "icon_mood": SP.IconMood.ENERGETIC,
        "prefer_diagram": SP.DiagramType.STEPS,
        "cover_pose": SP.Pose.POINTING,
        "cover_mood": SP.Mood.DARK,
        "hook_style": "เรื่องเล่าส่วนตัวที่นำไปสู่บทเรียน",
    },
]


class Command(BaseCommand):
    help = "สร้าง/อัปเดตโปรไฟล์ 5 มิติของ 6 กลุ่มลูกค้า จากข้อมูลในไฟล์ agent"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset", action="store_true",
            help="เขียนทับโปรไฟล์ที่มีอยู่แล้ว (ค่าที่เจ้าของแก้ไว้จะหายไป)",
        )

    def handle(self, *args, **options):
        reset = options["reset"]
        created_n = updated_n = skipped_n = 0

        for data in PROFILES:
            key = data["key"]
            obj = SegmentProfileOrNone(key)
            if obj is None:
                SP.objects.create(**data)
                created_n += 1
                self.stdout.write(self.style.SUCCESS("สร้าง  %s" % key))
            elif reset:
                for field, value in data.items():
                    setattr(obj, field, value)
                obj.save()
                updated_n += 1
                self.stdout.write(self.style.WARNING("เขียนทับ %s" % key))
            else:
                skipped_n += 1
                self.stdout.write("ข้าม   %s (มีอยู่แล้ว)" % key)

        self.stdout.write(self.style.SUCCESS(
            "\nสร้าง %d · เขียนทับ %d · ข้าม %d · รวมในระบบ %d กลุ่ม"
            % (created_n, updated_n, skipped_n, SP.objects.count())
        ))


def SegmentProfileOrNone(key):
    return SP.objects.filter(key=key).first()
