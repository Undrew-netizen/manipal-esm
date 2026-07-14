from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    faculty = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("faculty", "name")

    def __str__(self):
        return self.name
