from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

class BasicSignupForm(SignupForm):
  
   def save(self, request):
       user = super(BasicSignupForm, self).save(request)
       basic_group = Group.objects.get_or_create(name='common')[0]
       basic_group.user_set.add(user)
       user.save()
       return user
