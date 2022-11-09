from django.contrib import admin
from qbank.models import ExamHeader, ExamQuestion, Category

from django.urls import reverse
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin

# Register your models here.


@admin.register(ExamHeader)
class ExamAdmin(SummernoteModelAdmin):
    list_display = ("exam_id", "name", "desc", )
    summernote_fields = ('desc',)

    class Meta:
        ordering = ("exam_id", "name")

    pass




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("category_id", "category_name", "description")

    

    class Meta:
        ordering = ("category_id", "category_name")

    pass


@admin.register(ExamQuestion)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_id", 'question_num',
                    "question", "answer", "link_to_exam")
    list_filter = ('exam_ref', 'question_num')

    def link_to_exam(self, obj):
        link = reverse("admin:qbank_examheader_change", args=[
                       obj.exam_ref.exam_id])  # model name has to be lowercase
        return format_html('<a href="{}">{}</a>', link, obj.exam_ref.name)
        # return u'<a href="%s">%s</a>' % (link,obj.exam_ref.name)
    link_to_exam.allow_tags = True

    class Meta:
        ordering = ("question_num")

    pass
