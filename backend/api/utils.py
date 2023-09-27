from django.db.models import Sum
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from recipes.models import IngredientRecipe


def download_shop_cart(user):
    """Функция для скачивания списка ингредиентов из списка покупок."""
    shop_ingredients = (
        IngredientRecipe.objects
        .filter(recipe__shoplist__user=user)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(sum_amount=Sum('amount'))
        .order_by('-sum_amount')
    )
    file = HttpResponse(content_type='application/pdf')
    file['Content-Disposition'] = 'attachment; filename=shoplist.pdf'
    shoplist = canvas.Canvas(file)
    pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSansCondensed.ttf'))
    shoplist.setFont('DejaVu', 14)
    height = 800
    shoplist.drawString(40, height, 'Список покупок:')
    height -= 40
    count = 1
    for ingredient in shop_ingredients:
        if height < 70:
            shoplist.showPage()
            height = 800
        shoplist.drawString(40, height, (
            f'{count}. {ingredient["ingredient__name"]} - '
            f'{ingredient["sum_amount"]} '
            f'{ingredient["ingredient__measurement_unit"]}'
        ))
        count += 1
        height -= 20
    if height < 80:
        shoplist.showPage()
        height = 830
    shoplist.drawString(40, height - 30,
                        'Спасибо за использование сервиса Foodgram.')
    shoplist.showPage()
    shoplist.save()
    return file
