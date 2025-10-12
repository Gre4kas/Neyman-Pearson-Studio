// Улучшения отображения контента - изображения и таблицы
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    console.log('Загружены улучшения отображения контента');

    // Функция для применения улучшений к контенту
    function enhanceContent(container) {
        if (!container) return;

        const $container = container instanceof jQuery ? container : $(container);

        // Обработка изображений
        $container.find('img').each(function () {
            const $img = $(this);
            const $figure = $img.closest('figure');
            const $parent = $img.parent();

            // Базовые стили для всех изображений
            $img.css({
                'max-width': '100%',
                'height': 'auto',
                'border-radius': '6px',
                'box-shadow': '0 4px 12px rgba(0,0,0,0.15)',
                'transition': 'transform 0.2s ease'
            });

            // Если изображение в figure
            if ($figure.length && $figure.hasClass('image')) {
                $figure.css({
                    'text-align': 'center',
                    'margin': '25px 0',
                    'clear': 'both'
                });

                $img.css({
                    'display': 'block',
                    'margin': '0 auto'
                });
            }

            // Обработка классов выравнивания
            const imgClass = $img.attr('class') || '';
            const parentStyle = $parent.attr('style') || '';

            if (imgClass.includes('image-style-align-left')) {
                $img.css({
                    'float': 'left',
                    'margin': '10px 20px 10px 0',
                    'max-width': '50%'
                });
            } else if (imgClass.includes('image-style-align-right')) {
                $img.css({
                    'float': 'right',
                    'margin': '10px 0 10px 20px',
                    'max-width': '50%'
                });
            } else if (imgClass.includes('image-style-align-center') ||
                parentStyle.includes('text-align: center') ||
                parentStyle.includes('text-align:center')) {
                $img.css({
                    'display': 'block',
                    'margin': '20px auto',
                    'float': 'none'
                });
            }
        });

        // Обработка таблиц
        $container.find('table').each(function () {
            const $table = $(this);
            const $figure = $table.closest('figure');

            // Базовые стили для таблиц
            $table.css({
                'width': '100%',
                'border-collapse': 'collapse',
                'margin': '25px 0',
                'font-size': '14px',
                'box-shadow': '0 4px 12px rgba(0,0,0,0.1)',
                'border-radius': '8px',
                'overflow': 'hidden',
                'background': '#fff'
            });

            // Если таблица в figure
            if ($figure.length && $figure.hasClass('table')) {
                $figure.css({
                    'text-align': 'center',
                    'margin': '25px 0',
                    'clear': 'both',
                    'overflow-x': 'auto'
                });

                $table.css({
                    'display': 'inline-block',
                    'text-align': 'left',
                    'margin': '0 auto'
                });
            }

            // Стили заголовков
            $table.find('th').css({
                'background': 'linear-gradient(135deg, #495057 0%, #6c757d 100%)',
                'color': 'white',
                'padding': '15px 12px',
                'font-weight': '600',
                'font-size': '13px',
                'text-transform': 'uppercase',
                'letter-spacing': '0.5px',
                'border': 'none'
            });

            // Стили ячеек
            $table.find('td').css({
                'padding': '12px',
                'border-bottom': '1px solid #e9ecef',
                'border-left': 'none',
                'border-right': 'none',
                'border-top': 'none'
            });

            // Чередующиеся строки
            $table.find('tbody tr:even').css('background', '#f8f9fa');

            // Эффекты при наведении
            $table.find('tbody tr').hover(
                function () {
                    $(this).css('background', '#e3f2fd');
                },
                function () {
                    const index = $(this).index();
                    $(this).css('background', index % 2 === 1 ? '#f8f9fa' : 'transparent');
                }
            );
        });

        // Обработка центрированных контейнеров
        $container.find('[style*="text-align: center"], [style*="text-align:center"]').each(function () {
            const $element = $(this);
            $element.find('img, table').css({
                'display': 'block',
                'margin': '20px auto'
            });
        });

        // Очистка float элементов
        $container.append('<div style="clear: both;"></div>');
    }

    // Применяем улучшения при загрузке
    enhanceContent('#article-content');
    enhanceContent('#live-preview-content');
    enhanceContent('.preview-content-area');

    // Для админки - следим за изменениями в предпросмотре
    if (window.location.pathname.includes('/admin/')) {
        console.log('Режим админки - настраиваем отслеживание изменений');

        // Создаем наблюдатель за изменениями DOM
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function (node) {
                        if (node.nodeType === 1) { // Element node
                            const $node = $(node);

                            // Если добавлен элемент с изображениями или таблицами
                            if ($node.find('img, table').length > 0 ||
                                $node.is('img, table, figure')) {
                                console.log('Обнаружены новые изображения/таблицы, применяем улучшения');
                                enhanceContent($node);
                                enhanceContent($node.parent());
                            }
                        }
                    });
                }
            });
        });

        // Отслеживаем изменения в области предпросмотра
        const previewArea = document.querySelector('#live-preview-content');
        if (previewArea) {
            observer.observe(previewArea, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });
            console.log('Настроено отслеживание изменений в области предпросмотра');
        }

        // Периодическая проверка и улучшение контента
        setInterval(function () {
            enhanceContent('#live-preview-content');
            enhanceContent('.preview-content-area');
        }, 3000);
    }

    // Улучшения при загрузке MathJax
    if (window.MathJax) {
        // После рендеринга формул применяем улучшения
        window.MathJax.startup.promise.then(function () {
            console.log('MathJax загружен, применяем улучшения контента');
            setTimeout(function () {
                enhanceContent('#article-content');
                enhanceContent('#live-preview-content');
            }, 500);
        });
    }

    // Экспортируем функцию для использования в других скриптах
    window.enhanceContent = enhanceContent;

    console.log('Улучшения отображения контента инициализированы');
});

// Дополнительные улучшения для мобильных устройств
function adjustForMobile() {
    const isMobile = window.innerWidth <= 768;

    if (isMobile) {
        // На мобильных убираем float для изображений
        $('img.image-style-align-left, img.image-style-align-right').each(function () {
            const $img = $(this);
            $img.css({
                'float': 'none',
                'display': 'block',
                'margin': '20px auto',
                'max-width': '100%'
            });
        });

        // Улучшаем отображение таблиц на мобильных
        $('table').each(function () {
            const $table = $(this);
            const $wrapper = $table.closest('figure.table');

            if ($wrapper.length) {
                $wrapper.css({
                    'overflow-x': 'auto',
                    '-webkit-overflow-scrolling': 'touch'
                });
            } else {
                $table.wrap('<div style="overflow-x: auto; -webkit-overflow-scrolling: touch;"></div>');
            }
        });
    }
}

// Вызываем при загрузке и изменении размера окна
$(document).ready(adjustForMobile);
$(window).on('resize', adjustForMobile);