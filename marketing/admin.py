from django.contrib import admin
from .models import (Campaign, Keyword, ContentBacklog, SegmentProfile,
                     SlopPattern, ContentScore, ExpertScore)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "channel", "budget", "kpi_leads", "actual_leads", "status", "start_date"]
    list_filter = ["channel", "status"]
    search_fields = ["name"]

@admin.register(ContentBacklog)
class ContentBacklogAdmin(admin.ModelAdmin):
    list_display = ["num", "topic", "keyword", "priority", "status", "owner"]
    list_filter = ["priority", "status"]
    search_fields = ["topic", "keyword"]
    list_editable = ["status", "priority"]

@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["keyword", "intent", "search_volume", "difficulty", "current_rank", "target_position"]
    list_filter = ["intent"]
    search_fields = ["keyword"]


@admin.register(SegmentProfile)
class SegmentProfileAdmin(admin.ModelAdmin):
    """โปรไฟล์ 5 มิติต่อกลุ่มลูกค้า — แก้ที่นี่ได้จนกว่าหน้า /owner/segments/ จะเสร็จ"""
    list_display = ["name", "key", "pen_name", "agent_slug", "prefer_diagram", "cover_pose", "is_active"]
    list_filter = ["is_active", "shape", "icon_mood", "prefer_diagram", "cover_pose"]
    search_fields = ["key", "name", "pen_name", "agent_slug"]
    fieldsets = (
        ("ตัวระบุ", {"fields": ("key", "name", "agent_slug", "pen_name", "pronoun", "is_active")}),
        ("1. โทนการเขียน", {"fields": ("tone", "reader")}),
        ("2. แหล่งค้นข้อมูล", {"fields": ("research",)}),
        ("3. สไตล์ diagram", {
            "fields": ("shape", "accent_secondary", "icon_mood", "prefer_diagram"),
            "description": "สีแบรนด์กรม #0F172A + ทอง #C9A84C ห้ามเปลี่ยน ตรงนี้คือสีรองเท่านั้น",
        }),
        ("4. ภาพปก", {"fields": ("cover_pose", "cover_mood")}),
        ("5. รูปแบบ hook", {"fields": ("hook_style",)}),
        ("อื่น ๆ", {"fields": ("notes",)}),
    )


@admin.register(SlopPattern)
class SlopPatternAdmin(admin.ModelAdmin):
    """รายการ AI-slop ภาษาไทย — เพิ่มได้เรื่อย ๆ เมื่อเจอของจริง"""
    list_display = ["pattern", "kind", "penalty", "hit_count", "is_active"]
    list_filter = ["kind", "penalty", "is_active"]
    search_fields = ["pattern", "why", "fix"]
    list_editable = ["is_active"]
    ordering = ["-hit_count", "-penalty"]
    fieldsets = (
        ("สิ่งที่จับ", {"fields": ("pattern", "kind", "penalty", "is_active")}),
        ("อธิบายให้นักเขียนเข้าใจ", {
            "fields": ("why", "fix"),
            "description": "บอกเหตุผลเสมอ ห้ามบอกแค่ว่าห้าม ไม่งั้นนักเขียนจะเลี่ยงคำแต่เขียนแบบเดิม",
        }),
        ("ตัวอย่าง", {"fields": ("example_bad", "example_ok")}),
        ("สถิติ", {"fields": ("hit_count",)}),
    )
    readonly_fields = ["hit_count"]


class ExpertScoreInline(admin.TabularInline):
    model = ExpertScore
    extra = 0
    fields = ["round_no", "expert", "score", "weight", "feedback"]
    ordering = ["round_no", "-weight"]


@admin.register(ContentScore)
class ContentScoreAdmin(admin.ModelAdmin):
    list_display = ["article", "aggregate", "status", "rounds", "approved_at"]
    list_filter = ["status", "rubric", "segment"]
    search_fields = ["article__title"]
    inlines = [ExpertScoreInline]
    readonly_fields = ["created_at"]
    fieldsets = (
        ("บทความ", {"fields": ("article", "segment", "rubric")}),
        ("ผลคะแนน", {"fields": ("aggregate", "rounds", "status", "panel")}),
        ("สิ่งที่ต้องแก้", {"fields": ("weaknesses", "slop_hits")}),
        ("การอนุมัติ", {
            "fields": ("approved_by", "approved_at"),
            "description": "คะแนนผ่านไม่เท่ากับอนุมัติ — บทความจะเผยแพร่ได้ต้องมีคนกดอนุมัติที่นี่หรือที่ /owner/content-quality/",
        }),
        ("อื่น ๆ", {"fields": ("created_at",)}),
    )
