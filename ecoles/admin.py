from django.contrib import admin
from .models import Ecole, Category, Field, Specialization, Course, Module, Submodule, Assignment, Task, AssignmentNote


admin.site.register(Ecole)
admin.site.register(Category)
admin.site.register(Field)
admin.site.register(Specialization)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Submodule)
admin.site.register(Assignment)
admin.site.register(Task)
admin.site.register(AssignmentNote)

