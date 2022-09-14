from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 


class Skill(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(blank=True, null=True)
    skill_type = models.CharField(
        max_length=64, 
        choices=(
            ("General Skill", "General Skill"), 
            ("Foreign Language", "Foreign Language"),
            ("Programming Language", "Programming Language"),
            ("Programming Library or Framework", "Programming Library or Framework"), 
            ("Survival Skill", "Survival Skill"),
            # etc....
        ),
        default="General Skill",
        blank=False,
    )
    # Use ManyToMany for students? Or instead new model so you can include proficiency % for each user?

    def __str__(self):
        return self.name


class SkillProgress(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skill_fk")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_learning_skill")
    progress = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])


# class Operation
# start_date = 
# end_date = 

# class OperationalObjective
# deadline
# start_date/end_date not needed because they are contained within operation.

# class OperationalAssignment
# start_date = 
# end_date = 


