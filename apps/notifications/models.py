from django.db import models


class EmailQueue(models.Model):
    email_id = models.AutoField(primary_key=True)
    to_email = models.CharField(max_length=150)
    to_name = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=300)
    body_html = models.TextField()
    body_text = models.TextField(blank=True, null=True)
    attachment_path = models.CharField(max_length=500, blank=True, null=True)
    priority = models.CharField(
        max_length=6, default='Normal',
        choices=[('High', 'High'), ('Normal', 'Normal'), ('Low', 'Low')]
    )
    status = models.CharField(
        max_length=8, default='Queued',
        choices=[
            ('Queued', 'Queued'), ('Sent', 'Sent'),
            ('Failed', 'Failed'), ('Retrying', 'Retrying'),
        ]
    )
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.IntegerField(null=True, blank=True)
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_queue'
        ordering = ['-created_at']


class GeneratedDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    document_type = models.CharField(max_length=30)
    reference_type = models.CharField(max_length=50, blank=True, null=True)
    reference_id = models.IntegerField(null=True, blank=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField(null=True, blank=True)
    generated_for = models.IntegerField(null=True, blank=True)
    generated_by = models.ForeignKey(
        'core.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    branch = models.ForeignKey('core.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'generated_documents'
        ordering = ['-created_at']


class ScheduledTaskLog(models.Model):
    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=9, default='Running',
        choices=[
            ('Running', 'Running'), ('Completed', 'Completed'), ('Failed', 'Failed'),
        ]
    )
    result_summary = models.TextField(blank=True, null=True)
    records_affected = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheduled_task_log'
        ordering = ['-started_at']