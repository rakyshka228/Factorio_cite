from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Tag(models.Model):
	name = models.CharField(max_length=40, unique=True)
	slug = models.SlugField(max_length=50, unique=True)

	class Meta:
		ordering = ('name',)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)
		super().save(*args, **kwargs)


class Blueprint(models.Model):
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blueprints')
	title = models.CharField(max_length=120)
	slug = models.SlugField(max_length=140, unique=True)
	description = models.TextField(max_length=2000)
	code = models.TextField()
	image = models.ImageField(upload_to='blueprints/', blank=True)
	tags = models.ManyToManyField(Tag, blank=True, related_name='blueprints')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('user_blueprint_detail', args=[self.pk])

	@property
	def like_count(self):
		return self.likes.count()

	@property
	def comment_count(self):
		return self.comments.count()


class Like(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	blueprint = models.ForeignKey(Blueprint, on_delete=models.CASCADE, related_name='likes')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=('user', 'blueprint'), name='one_like_per_user_blueprint'),
		]


class Comment(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	blueprint = models.ForeignKey(Blueprint, on_delete=models.CASCADE, related_name='comments')
	text = models.TextField(max_length=1000)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created_at',)
