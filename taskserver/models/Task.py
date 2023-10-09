import models


class TaskEntry(models.Model):
    key = models.CharField(max_length=120, primary_key=True)
    name = models.CharField(max_length=120, primary_key=True)
    file = models.CharField(max_length=4096, primary_key=True)

    class Meta:
        abstract = True


class Task(TaskEntry):
    desc = models.CharField(max_length=4096)
    #vars = models.CharField(max_length=120)
    #sources = models.CharField(max_length=20, unique=True)
    #generates = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
