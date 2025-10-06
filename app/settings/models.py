from django.db import models
from ckeditor.fields import RichTextField

class Settings(models.Model):
    telegram = models.CharField(
        max_length=255,
        verbose_name='Ссылка на Телеграм'
    )
    instagram = models.CharField(
        max_length=255,
        verbose_name='Ссылка на Инстаграм'
    )
    whatsapp = models.CharField(
        max_length=255,
        verbose_name='Ссылка на Ватсап'
    )
    title_banner = models.CharField(
        max_length=155,
        verbose_name='Заголовка на Баннере'
    )
    description_banner = RichTextField(
        verbose_name = 'Описание Баннера'
    )
    image_banner = models.ImageField(
        upload_to='settings',
        verbose_name='Фото на баннере'
    )
    about_title = models.CharField(
        max_length=155,
        verbose_name='Заголовка о нас'
    )
    description_about = RichTextField(
        verbose_name='Описание О нас'
    )
    image_about1= models.ImageField(
        upload_to='about',
        verbose_name='Фото о нас'
    )
    image_about2= models.ImageField(
        upload_to='about',
        verbose_name='Фото о нас'
    )
    end_about = RichTextField(
        verbose_name='Текст О нас'
    )
    title_catalog = models.CharField(
        max_length=155,
        verbose_name='Заголовка Каталог'
    )
    review = models.CharField(
        max_length=155,
        verbose_name='Отзывы'
    )
    description_review = RichTextField(
        verbose_name='Описание отзывов'
    )
    text_footer = RichTextField(
        verbose_name='Описание Футера'
    )

    def __str__(self):
        return self.title_banner

    class Meta:
        verbose_name = 'Настройки'
        verbose_name_plural = 'Настройки Сайта'