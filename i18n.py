"""All interface text, in English and Arabic."""

LANGUAGES = {'ar': 'العربية', 'en': 'English'}

STRINGS = {
    'en': {
        'title': 'Salla Out-of-Stock Checker',
        'intro': 'Find the products listed on Salla that no longer have a sticker in the ERP.',
        'instructions': (
            '1. Upload the **Salla Product Quantities** CSV in the first box.\n'
            '2. Upload the **ERP sticker** CSV in the second box.\n'
            '3. Click **Process Files**, check the preview, then download the result.'
        ),
        'privacy': 'Your files are used only to produce this result and are not saved.',
        'salla_label': 'File 1: Salla Product Quantities (CSV)',
        'erp_label': 'File 2: ERP stickers (CSV)',
        'selected_file': 'Selected: {name}',
        'process': 'Process Files',
        'processing': 'Processing your files...',
        'success': 'Done. Found {count:,} out-of-stock products.',
        'metric_total': 'Salla products',
        'metric_checked': 'Checked',
        'metric_out_of_stock': 'Out of stock',
        'metric_skipped': 'Skipped',
        'preview': 'Preview',
        'download': 'Download result (CSV)',
        'skipped_warning': (
            '{count:,} products could not be checked because no number could be read '
            'from the end of their SKU. They are not in the downloaded file.'
        ),
        'skipped_list': 'Show skipped products',
        'no_match_warning': (
            'None of the Salla products were found in the ERP file, so every checked '
            'product is listed as out of stock. Please check that these are the right files.'
        ),
        'file_problem': 'Problem with {name}: {message}',
        'error_empty': 'the file is empty.',
        'error_unreadable': 'the file could not be read as a CSV.',
        'error_encoding': (
            'the file has an unsupported text encoding. '
            'In Excel, use Save As and choose "CSV UTF-8".'
        ),
        'error_missing_column_salla': (
            'the "sku_number" column was not found on row 2. '
            'Please upload the Salla Product Quantities export.'
        ),
        'error_missing_column_erp': (
            'the "sticker_number" column was not found on row 1. '
            'Please upload the ERP sticker export.'
        ),
        'error_swapped': 'this looks like the other file. Please swap the two uploads.',
        'error_no_stickers': 'no valid sticker numbers were found in this file.',
        'error_unexpected': 'Something went wrong while processing the files. Please check them and try again.',
        'error_details': 'Technical details',
    },
    'ar': {
        'title': 'فحص المنتجات غير المتوفرة في سلة',
        'intro': 'اعرف المنتجات المعروضة في سلة التي لم يعد لها ملصق في نظام ERP.',
        'instructions': (
            '1. ارفع ملف CSV الخاص بـ **كميات منتجات سلة** في الخانة الأولى.\n'
            '2. ارفع ملف CSV الخاص بـ **ملصقات ERP** في الخانة الثانية.\n'
            '3. اضغط **معالجة الملفات**، وراجع المعاينة، ثم نزّل النتيجة.'
        ),
        'privacy': 'تُستخدم ملفاتك لإنتاج هذه النتيجة فقط ولا يتم حفظها.',
        'salla_label': 'الملف 1: كميات منتجات سلة (CSV)',
        'erp_label': 'الملف 2: ملصقات ERP (CSV)',
        'selected_file': 'الملف المحدد: {name}',
        'process': 'معالجة الملفات',
        'processing': 'جارٍ معالجة الملفات...',
        'success': 'تمت المعالجة. عدد المنتجات غير المتوفرة: {count:,}.',
        'metric_total': 'منتجات سلة',
        'metric_checked': 'تم فحصها',
        'metric_out_of_stock': 'غير متوفرة',
        'metric_skipped': 'تم تخطيها',
        'preview': 'معاينة',
        'download': 'تنزيل النتيجة (CSV)',
        'skipped_warning': (
            'تعذر فحص {count:,} منتج لأنه لم يمكن قراءة رقم من نهاية رمز SKU الخاص بها. '
            'هذه المنتجات غير موجودة في الملف الذي سيتم تنزيله.'
        ),
        'skipped_list': 'عرض المنتجات التي تم تخطيها',
        'no_match_warning': (
            'لم يتم العثور على أي من منتجات سلة في ملف ERP، لذلك ظهرت كل المنتجات التي تم '
            'فحصها على أنها غير متوفرة. يرجى التأكد من صحة الملفات.'
        ),
        'file_problem': 'مشكلة في الملف {name}: {message}',
        'error_empty': 'الملف فارغ.',
        'error_unreadable': 'تعذرت قراءة الملف بصيغة CSV.',
        'error_encoding': (
            'ترميز النص في الملف غير مدعوم. '
            'في Excel، اختر «حفظ باسم» ثم «CSV UTF-8».'
        ),
        'error_missing_column_salla': (
            'لم يتم العثور على العمود "sku_number" في الصف 2. '
            'يرجى رفع ملف كميات منتجات سلة.'
        ),
        'error_missing_column_erp': (
            'لم يتم العثور على العمود "sticker_number" في الصف 1. '
            'يرجى رفع ملف ملصقات ERP.'
        ),
        'error_swapped': 'يبدو أن هذا هو الملف الآخر. يرجى تبديل الملفين.',
        'error_no_stickers': 'لم يتم العثور على أرقام ملصقات صالحة في هذا الملف.',
        'error_unexpected': 'حدث خطأ أثناء معالجة الملفات. يرجى التحقق منها والمحاولة مرة أخرى.',
        'error_details': 'تفاصيل تقنية',
    },
}


def t(lang, key, **kwargs):
    """Returns the text for `key` in `lang`, filled in with any format values."""
    text = STRINGS[lang][key]
    return text.format(**kwargs) if kwargs else text
