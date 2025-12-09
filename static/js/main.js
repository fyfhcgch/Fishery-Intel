// 渔智汇自定义JavaScript

// 初始化页面
function initializePage() {
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
}

// 绑定事件监听器
function bindEventListeners() {
    // 可以在这里添加其他事件监听器
}

// 初始化图表
function initializeCharts() {
    // 初始化水质仪表盘
    initializeWaterQualityGauges();
    
    // 初始化趋势图表
    initializeTrendCharts();
    
    // 初始化数据对比图表
    initializeComparisonCharts();
    
    // 初始化预测图表
    initializePredictionCharts();
}

// 初始化水质仪表盘
function initializeWaterQualityGauges() {
    // 创建或更新温度仪表盘
    if ($('#temperature-gauge').length) {
        window.tempGauge = createWaterQualityGauge('temperature-gauge', 26, 0, 40, 20, 15, '温度°C');
    }
    
    // 创建或更新pH值仪表盘
    if ($('#ph-gauge').length) {
        window.phGauge = createWaterQualityGauge('ph-gauge', 7.8, 0, 14, 7.0, 6.5, 'pH值');
    }
    
    // 创建或更新溶解氧仪表盘
    if ($('#oxygen-gauge').length) {
        window.oxygenGauge = createWaterQualityGauge('oxygen-gauge', 7.5, 0, 15, 5, 3, '溶解氧mg/L');
    }
    
    // 创建或更新氨氮仪表盘
    if ($('#ammonia-gauge').length) {
        window.ammoniaGauge = createWaterQualityGauge('ammonia-gauge', 0.2, 0, 2, 0.5, 1.0, '氨氮mg/L');
    }
}

// 更新水质仪表盘数据
function updateWaterQualityGauges(tempValue, phValue, oxygenValue, ammoniaValue) {
    // 更新温度仪表盘
    if (window.tempGauge) {
        updateGaugeValue(window.tempGauge, tempValue, 0, 40, 20, 15, '温度°C');
    }
    
    // 更新pH值仪表盘
    if (window.phGauge) {
        updateGaugeValue(window.phGauge, phValue, 0, 14, 7.0, 6.5, 'pH值');
    }
    
    // 更新溶解氧仪表盘
    if (window.oxygenGauge) {
        updateGaugeValue(window.oxygenGauge, oxygenValue, 0, 15, 5, 3, '溶解氧mg/L');
    }
    
    // 更新氨氮仪表盘
    if (window.ammoniaGauge) {
        updateGaugeValue(window.ammoniaGauge, ammoniaValue, 0, 2, 0.5, 1.0, '氨氮mg/L');
    }
}

// 更新仪表盘数值
function updateGaugeValue(gauge, value, minValue, maxValue, warningThreshold, dangerThreshold, label) {
    // 确定颜色
    var color;
    if (value < dangerThreshold) {
        color = '#F5222D'; // 危险 - 红色
    } else if (value < warningThreshold) {
        color = '#FAAD14'; // 警告 - 黄色
    } else {
        color = '#52C41A'; // 正常 - 绿色
    }
    
    // 更新数据
    gauge.data.datasets[0].data = [value, maxValue - value];
    gauge.data.datasets[0].backgroundColor = [color, '#F0F0F0'];
    gauge.update();
    
    // 更新中心文本
    var chartCtx = gauge.ctx;
    var width = gauge.width;
    var height = gauge.height;
    
    chartCtx.clearRect(0, 0, width, height);
    gauge.draw();
    
    // 重新绘制中心文本
    chartCtx.restore();
    var fontSize = (height / 114).toFixed(2);
    chartCtx.font = "bold " + fontSize + "em sans-serif";
    chartCtx.textBaseline = "middle";
    chartCtx.fillStyle = color;
    
    var text = value;
    var textX = Math.round((width - chartCtx.measureText(text).width) / 2);
    var textY = height / 2 + 10;
    
    chartCtx.fillText(text, textX, textY);
    
    // 添加标签
    chartCtx.font = (fontSize * 0.6) + "em sans-serif";
    chartCtx.fillStyle = '#666';
    var labelX = Math.round((width - chartCtx.measureText(label).width) / 2);
    var labelY = height / 2 + 30;
    
    chartCtx.fillText(label, labelX, labelY);
    chartCtx.save();
}

// 初始化趋势图表
function initializeTrendCharts() {
    // 检查页面是否有趋势图元素
    if ($('#temperature-trend').length) {
        // 生成模拟数据
        var tempData = generateMockTrendData(24, 25, 28); // 24小时，25-28度范围
        
        // 创建温度趋势图
        createTrendChart('temperature-trend', tempData, '温度', '#1890FF');
    }
    
    if ($('#ph-trend').length) {
        // 生成模拟数据
        var phData = generateMockTrendData(24, 7.5, 8.0); // 24小时，7.5-8.0范围
        
        // 创建pH趋势图
        createTrendChart('ph-trend', phData, 'pH值', '#52C41A');
    }
    
    if ($('#oxygen-trend').length) {
        // 生成模拟数据
        var oxygenData = generateMockTrendData(24, 6.5, 8.0); // 24小时，6.5-8.0范围
        
        // 创建溶解氧趋势图
        createTrendChart('oxygen-trend', oxygenData, '溶解氧', '#13C2C2');
    }
}

// 初始化数据对比图表
function initializeComparisonCharts() {
    // 检查页面是否有对比图表元素
    if ($('#pond-comparison').length) {
        createPondComparisonChart();
    }
    
    if ($('#parameter-comparison').length) {
        createParameterComparisonChart();
    }
}

// 初始化预测图表
function initializePredictionCharts() {
    // 检查页面是否有预测图表元素
    if ($('#prediction-chart').length) {
        createPredictionChart();
    }
}

// 生成模拟趋势数据
function generateMockTrendData(hours, minValue, maxValue) {
    var data = [];
    var now = new Date();
    
    for (var i = hours; i >= 0; i--) {
        var timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
        var value = minValue + Math.random() * (maxValue - minValue);
        
        // 添加一些趋势变化
        if (i < hours / 2) {
            value += (maxValue - minValue) * 0.1 * Math.sin(i / 3);
        }
        
        data.push({
            timestamp: timestamp,
            value: parseFloat(value.toFixed(1))
        });
    }
    
    return data;
}

// 设置自动刷新
function setupAutoRefresh() {
    // 自动刷新数据（每5分钟）
    var refreshInterval = 5 * 60 * 1000; // 5分钟
    var refreshTimer;
    
    // 页面可见性检测
    function handleVisibilityChange() {
        if (document.hidden) {
            // 页面隐藏时清除定时器
            if (refreshTimer) {
                clearInterval(refreshTimer);
                refreshTimer = null;
            }
        } else {
            // 页面可见时重新启动定时器
            if (!refreshTimer) {
                refreshTimer = setInterval(refreshData, refreshInterval);
            }
            // 页面重新可见时立即刷新一次数据
            refreshData();
        }
    }
    
    // 添加页面可见性事件监听器
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // 启动定时器
    refreshTimer = setInterval(refreshData, refreshInterval);
    
    // 存储定时器引用，以便后续可以停止
    window.dataRefreshTimer = refreshTimer;
}

// 停止自动刷新
function stopAutoRefresh() {
    if (window.dataRefreshTimer) {
        clearInterval(window.dataRefreshTimer);
        window.dataRefreshTimer = null;
    }
    // 移除页面可见性事件监听器
    document.removeEventListener('visibilitychange', handleVisibilityChange);
}

// 重启自动刷新
function restartAutoRefresh() {
    stopAutoRefresh();
    setupAutoRefresh();
}

$(document).ready(function() {
    // 初始化页面
    initializePage();
    
    // 检查用户偏好设置
    checkUserPreferences();
    
    // 添加深色模式切换按钮
    addDarkModeToggle();
    
    // 触摸交互优化
    optimizeTouchInteractions();
    
    // 添加移动端特定优化
    addMobileOptimizations();
    
    // 添加下拉刷新支持
    addPullToRefresh();
    
    // 添加页面加载动画
    animatePageLoad();
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 初始化图表
    initializeCharts();
    
    // 设置自动刷新
    setupAutoRefresh();
});

// 刷新数据
function refreshData() {
    // 获取最新水质数据
    $.get('/data/api/latest_water_quality')
        .done(function(data) {
            updateWaterQualityDisplay(data);
        })
        .fail(function(xhr, status, error) {
            console.error('获取最新水质数据失败:', error);
            showToast('获取水质数据失败，请稍后重试', 'error');
        });
    
    // 检查新的预警
    $.post('/alert/check_alerts')
        .done(function(data) {
            if (data.success && data.new_alerts.length > 0) {
                showNewAlertsNotification(data.new_alerts);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('检查新预警失败:', error);
            // 不显示错误提示给用户，因为这是一个后台检查功能
        });
}

// 更新水质数据显示
function updateWaterQualityDisplay(data) {
    for (var pondId in data) {
        var pondData = data[pondId];
        var pondElement = $('#pond-' + pondId);
        
        if (pondElement.length) {
            // 更新溶解氧
            pondElement.find('.do-value').text(pondData.dissolved_oxygen + ' mg/L');
            updateStatusIndicator(pondElement.find('.do-indicator'), pondData.dissolved_oxygen, 4.5, 3.5);
            
            // 更新温度
            pondElement.find('.temp-value').text(pondData.temperature + ' °C');
            
            // 更新pH
            pondElement.find('.ph-value').text(pondData.ph);
            updateStatusIndicator(pondElement.find('.ph-indicator'), pondData.ph, 6.5, 8.5, true);
            
            // 更新氨氮
            pondElement.find('.ammonia-value').text(pondData.ammonia + ' mg/L');
            updateStatusIndicator(pondElement.find('.ammonia-indicator'), pondData.ammonia, 0.4, 0.6, false, true);
            
            // 更新时间戳
            var timestamp = new Date(pondData.timestamp);
            pondElement.find('.timestamp').text(formatTimeAgo(timestamp));
        }
    }
    
    // 如果是主仪表盘页面，同时更新仪表盘
    if ($('.dashboard-page').length > 0 && Object.keys(data).length > 0) {
        // 使用第一个塘口的数据更新仪表盘
        var firstPondId = Object.keys(data)[0];
        var firstPondData = data[firstPondId];
        
        // 更新仪表盘数据
        updateWaterQualityGauges(
            firstPondData.temperature,
            firstPondData.ph,
            firstPondData.dissolved_oxygen,
            firstPondData.ammonia
        );
    }
}

// 更新状态指示器
function updateStatusIndicator(element, value, warningThreshold, dangerThreshold, isRange = false, isInverse = false) {
    element.removeClass('normal warning danger');
    
    var isWarning = false;
    var isDanger = false;
    
    if (isRange) {
        // 对于pH值，检查是否在范围内
        isWarning = value < warningThreshold || value > dangerThreshold;
    } else {
        // 对于其他指标，检查是否低于阈值
        if (isInverse) {
            // 对于氨氮，值越高越差
            isWarning = value > warningThreshold;
            isDanger = value > dangerThreshold;
        } else {
            // 对于溶解氧，值越低越差
            isWarning = value < warningThreshold;
            isDanger = value < dangerThreshold;
        }
    }
    
    if (isDanger) {
        element.addClass('danger');
    } else if (isWarning) {
        element.addClass('warning');
    } else {
        element.addClass('normal');
    }
}

// 显示新预警通知
function showNewAlertsNotification(alerts) {
    alerts.forEach(function(alert) {
        var alertClass = 'alert-' + (alert.level === 'danger' ? 'danger' : alert.level === 'warning' ? 'warning' : 'info');
        var alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <strong>${alert.pond_name} - ${alert.title}</strong><br>
                ${alert.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        $('#alerts-container').prepend(alertHtml);
    });
    
    // 更新预警计数
    var currentCount = parseInt($('#alert-count').text()) || 0;
    $('#alert-count').text(currentCount + alerts.length);
}

// 格式化时间差
function formatTimeAgo(date) {
    var seconds = Math.floor((new Date() - date) / 1000);
    
    var interval = Math.floor(seconds / 31536000);
    if (interval > 1) return interval + " " + gettext("years ago");
    
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) return interval + " " + gettext("months ago");
    
    interval = Math.floor(seconds / 86400);
    if (interval > 1) return interval + " " + gettext("days ago");
    
    interval = Math.floor(seconds / 3600);
    if (interval > 1) return interval + " " + gettext("hours ago");
    
    interval = Math.floor(seconds / 60);
    if (interval > 1) return interval + " " + gettext("minutes ago");
    
    return gettext("just now");
}

// 页面加载动画
function animatePageLoad() {
    // 添加淡入动画到主要内容区域
    $('main').addClass('fade-in');
    
    // 为卡片添加滑入动画
    $('.card').each(function(index) {
        var $card = $(this);
        setTimeout(function() {
            $card.addClass('slide-in-up');
        }, index * 100);
    });
}

// 触摸交互优化
function optimizeTouchInteractions() {
    // 检测是否为触摸设备
    if ('ontouchstart' in window) {
        $('body').addClass('touch-device');
        
        // 为按钮添加触摸反馈
        $('.btn').on('touchstart', function() {
            $(this).addClass('touch-active');
            addTouchRipple(this);
        }).on('touchend', function() {
            var $this = $(this);
            setTimeout(function() {
                $this.removeClass('touch-active');
            }, 150);
        });
        
        // 为卡片添加触摸反馈
        $('.card').on('touchstart', function() {
            $(this).addClass('touch-active');
            addTouchRipple(this);
        }).on('touchend', function() {
            var $this = $(this);
            setTimeout(function() {
                $this.removeClass('touch-active');
            }, 150);
        });
        
        // 为导航链接添加触摸反馈
        $('.nav-link').on('touchstart', function() {
            $(this).addClass('touch-active');
        }).on('touchend', function() {
            var $this = $(this);
            setTimeout(function() {
                $this.removeClass('touch-active');
            }, 150);
        });
        
        // 为下拉菜单项添加触摸反馈
        $('.dropdown-item').on('touchstart', function() {
            $(this).addClass('touch-active');
        }).on('touchend', function() {
            var $this = $(this);
            setTimeout(function() {
                $this.removeClass('touch-active');
            }, 150);
        });
        
        // 添加长按支持
        addLongPressSupport();
        
        // 添加滑动手势支持
        addSwipeGestureSupport();
    }
}

// 添加触摸涟漪效果
function addTouchRipple(element) {
    var $element = $(element);
    var ripple = $('<span class="touch-ripple"></span>');
    
    // 获取触摸位置
    $element.on('touchstart', function(e) {
        var touch = e.originalEvent.touches[0];
        var rect = this.getBoundingClientRect();
        var size = Math.max(rect.width, rect.height);
        var x = touch.clientX - rect.left - size / 2;
        var y = touch.clientY - rect.top - size / 2;
        
        ripple.css({
            width: size + 'px',
            height: size + 'px',
            left: x + 'px',
            top: y + 'px'
        });
        
        $element.append(ripple);
        
        // 动画结束后移除涟漪
        setTimeout(function() {
            ripple.remove();
        }, 600);
    });
}

// 添加长按支持
function addLongPressSupport() {
    var pressTimer;
    var isLongPress = false;
    
    $('.long-press, .card, .data-card').on('touchstart', function(e) {
        var $this = $(this);
        isLongPress = false;
        
        pressTimer = setTimeout(function() {
            isLongPress = true;
            $this.addClass('active');
            
            // 震动反馈（如果支持）
            if ('vibrate' in navigator) {
                navigator.vibrate(50);
            }
            
            // 触发长按事件
            $this.trigger('longpress');
        }, 500);
    }).on('touchend', function() {
        clearTimeout(pressTimer);
        
        if (isLongPress) {
            var $this = $(this);
            setTimeout(function() {
                $this.removeClass('active');
            }, 200);
        }
    }).on('touchmove', function() {
        clearTimeout(pressTimer);
    });
}

// 添加滑动手势支持
function addSwipeGestureSupport() {
    var touchStartX = 0;
    var touchStartY = 0;
    var touchEndX = 0;
    var touchEndY = 0;
    var swipeElement = null;
    
    // 为可滑动元素添加滑动支持
    $('.swipe-container, .card, .data-card').on('touchstart', function(e) {
        swipeElement = this;
        touchStartX = e.originalEvent.touches[0].clientX;
        touchStartY = e.originalEvent.touches[0].clientY;
    }).on('touchend', function(e) {
        if (!swipeElement) return;
        
        touchEndX = e.originalEvent.changedTouches[0].clientX;
        touchEndY = e.originalEvent.changedTouches[0].clientY;
        
        handleSwipeGesture(swipeElement, touchStartX, touchStartY, touchEndX, touchEndY);
    });
    
    // 处理滑动手势
    function handleSwipeGesture(element, startX, startY, endX, endY) {
        var deltaX = endX - startX;
        var deltaY = endY - startY;
        var minSwipeDistance = 50;
        
        // 确保水平滑动距离大于垂直滑动距离
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            var direction = deltaX > 0 ? 'right' : 'left';
            
            // 触发滑动事件
            $(element).trigger('swipe', direction);
            
            // 如果是侧滑菜单，处理菜单操作
            if ($(element).hasClass('swipe-menu')) {
                handleSwipeMenu(element, direction);
            }
        }
    }
    
    // 处理侧滑菜单
    function handleSwipeMenu(element, direction) {
        var $content = $(element).find('.swipe-menu-content');
        var $actions = $(element).find('.swipe-menu-actions');
        
        if (direction === 'left') {
            // 向左滑动，显示操作按钮
            var actionsWidth = $actions.outerWidth();
            $content.css('transform', 'translateX(-' + actionsWidth + 'px)');
        } else {
            // 向右滑动，隐藏操作按钮
            $content.css('transform', 'translateX(0)');
        }
    }
}

// 添加移动端特定优化
function addMobileOptimizations() {
    if ('ontouchstart' in window) {
        // 优化移动端滚动
        optimizeMobileScrolling();
        
        // 添加移动端导航优化
        optimizeMobileNavigation();
        
        // 添加移动端手势支持
        addMobileGestureSupport();
        
        // 优化移动端表单输入
        optimizeMobileFormInputs();
        
        // 添加移动端性能优化
        addMobilePerformanceOptimizations();
    }
}

// 优化移动端滚动
function optimizeMobileScrolling() {
    // 为滚动容器添加平滑滚动
    $('.table-responsive, .modal-body, .chart-container').css({
        '-webkit-overflow-scrolling': 'touch',
        'overflow-scrolling': 'touch'
    });
    
    // 防止橡皮筋效果（过度滚动）
    document.body.addEventListener('touchmove', function(e) {
        var $target = $(e.target);
        
        // 允许在可滚动区域内滚动
        if ($target.closest('.table-responsive, .modal-body, .chart-container').length) {
            return;
        }
        
        // 防止页面整体过度滚动
        e.preventDefault();
    }, { passive: false });
}

// 优化移动端导航
function optimizeMobileNavigation() {
    // 为移动端导航添加滑动切换支持
    var touchStartX = 0;
    var touchEndX = 0;
    
    $(document).on('touchstart', function(e) {
        touchStartX = e.originalEvent.touches[0].clientX;
    });
    
    $(document).on('touchend', function(e) {
        touchEndX = e.originalEvent.changedTouches[0].clientX;
        handleSwipeNavigation();
    });
    
    function handleSwipeNavigation() {
        var swipeDistance = touchEndX - touchStartX;
        var minSwipeDistance = 100;
        
        // 检测是否为从左边缘开始的右滑
        if (touchStartX < 20 && swipeDistance > minSwipeDistance) {
            // 打开侧边栏或菜单
            $('.navbar-toggler').click();
        }
    }
}

// 添加移动端手势支持
function addMobileGestureSupport() {
    // 双击缩放禁用
    var lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        var now = Date.now();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // 长按复制禁用
    document.addEventListener('selectstart', function(e) {
        if ($(e.target).is('.btn, .nav-link, .card')) {
            e.preventDefault();
        }
    });
}

// 优化移动端表单输入
function optimizeMobileFormInputs() {
    // 为数字输入框添加数字键盘
    $('input[type="number"]').attr('inputmode', 'numeric');
    $('input[type="tel"]').attr('inputmode', 'tel');
    $('input[type="email"]').attr('inputmode', 'email');
    $('input[type="url"]').attr('inputmode', 'url');
    
    // 为搜索框添加搜索键盘
    $('input[type="search"]').attr('inputmode', 'search');
    
    // 优化输入框焦点体验
    $('.form-control, .form-select').on('focus', function() {
        // 滚动到视图中心
        this.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
}

// 添加移动端性能优化
function addMobilePerformanceOptimizations() {
    // 减少重绘和回流
    $('body').addClass('mobile-optimized');
    
    // 优化动画性能
    $('.card, .btn, .data-card').css({
        'will-change': 'transform',
        'backface-visibility': 'hidden'
    });
    
    // 延迟加载非关键图片
    if ('IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        $('.lazy').each(function() {
            imageObserver.observe(this);
        });
    }
}

// 添加深色模式切换按钮
function addDarkModeToggle() {
    // 检查是否已存在深色模式切换按钮
    if ($('#dark-mode-toggle').length === 0) {
        var darkModeToggle = `
            <button id="dark-mode-toggle" class="btn btn-outline-primary ms-2" onclick="toggleDarkMode()" title="切换深色模式">
                <i class="fas fa-moon" id="dark-mode-icon"></i>
            </button>
        `;
        
        // 添加到用户下拉菜单中
        $('.dropdown-menu').prepend('<li><hr class="dropdown-divider"></li>');
        $('.dropdown-menu').prepend('<li><a class="dropdown-item" href="#" onclick="toggleDarkMode(); return false;"><i class="fas fa-moon me-2"></i>切换深色模式</a></li>');
        
        // 或者添加到导航栏
        $('.navbar-nav.me-auto').append('<li class="nav-item"><a class="nav-link" href="#" onclick="toggleDarkMode(); return false;" title="切换深色模式"><i class="fas fa-moon"></i></a></li>');
        
        // 更新图标状态
        updateDarkModeIcon();
    }
}

// 更新深色模式图标
function updateDarkModeIcon() {
    var $icon = $('#dark-mode-icon, .fa-moon');
    if ($('body').hasClass('dark-mode')) {
        $icon.removeClass('fa-moon').addClass('fa-sun');
    } else {
        $icon.removeClass('fa-sun').addClass('fa-moon');
    }
}

// 下拉刷新支持
function addPullToRefresh() {
    if ('ontouchstart' in window) {
        var startY = 0;
        var isPulling = false;
        var pullDistance = 0;
        var maxPullDistance = 80;
        var $refreshIndicator = null;
        
        // 创建刷新指示器
        function createRefreshIndicator() {
            if ($refreshIndicator === null) {
                $refreshIndicator = $('<div id="refresh-indicator" class="position-fixed top-0 start-50 translate-middle-x bg-primary text-white rounded-circle p-3" style="z-index: 1050; top: 20px; display: none;"><i class="fas fa-sync-alt"></i></div>');
                $('body').append($refreshIndicator);
            }
        }
        
        $(document).on('touchstart', function(e) {
            if ($(window).scrollTop() === 0) {
                startY = e.originalEvent.touches[0].pageY;
                isPulling = true;
                createRefreshIndicator();
            }
        });
        
        $(document).on('touchmove', function(e) {
            if (isPulling) {
                var currentY = e.originalEvent.touches[0].pageY;
                pullDistance = currentY - startY;
                
                if (pullDistance > 0 && pullDistance < maxPullDistance * 2) {
                    var opacity = Math.min(pullDistance / maxPullDistance, 1);
                    var rotation = pullDistance * 2;
                    
                    $refreshIndicator.css({
                        'display': 'block',
                        'opacity': opacity,
                        'transform': 'translateX(-50%) rotate(' + rotation + 'deg)'
                    });
                }
            }
        });
        
        $(document).on('touchend', function() {
            if (isPulling) {
                if (pullDistance > maxPullDistance) {
                    // 触发刷新
                    $refreshIndicator.addClass('spin');
                    refreshData();
                    
                    setTimeout(function() {
                        $refreshIndicator.fadeOut();
                    }, 1000);
                } else {
                    $refreshIndicator.fadeOut();
                }
                
                isPulling = false;
                pullDistance = 0;
            }
        });
    }
}

// 检查用户偏好设置
function checkUserPreferences() {
    // 检查是否启用高对比度模式
    if (localStorage.getItem('highContrast') === 'true') {
        $('body').addClass('high-contrast');
    }
    
    // 检查是否启用大字体模式
    if (localStorage.getItem('largeFont') === 'true') {
        $('body').addClass('large-font');
    }
    
    // 检查是否启用深色模式
    if (localStorage.getItem('darkMode') === 'true' || 
        (localStorage.getItem('darkMode') === null && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        $('body').addClass('dark-mode');
    }
    
    // 更新深色模式图标
    updateDarkModeIcon();
}

// 切换高对比度模式
function toggleHighContrast() {
    $('body').toggleClass('high-contrast');
    localStorage.setItem('highContrast', $('body').hasClass('high-contrast'));
    showToast($('body').hasClass('high-contrast') ? '高对比度模式已开启' : '高对比度模式已关闭', 'info');
}

// 切换大字体模式
function toggleLargeFont() {
    $('body').toggleClass('large-font');
    localStorage.setItem('largeFont', $('body').hasClass('large-font'));
    showToast($('body').hasClass('large-font') ? '大字体模式已开启' : '大字体模式已关闭', 'info');
}

// 切换深色模式
function toggleDarkMode() {
    $('body').toggleClass('dark-mode');
    localStorage.setItem('darkMode', $('body').hasClass('dark-mode'));
    updateDarkModeIcon();
    showToast($('body').hasClass('dark-mode') ? '深色模式已开启' : '深色模式已关闭', 'info');
}

// 创建水质仪表盘
function createWaterQualityGauge(canvasId, value, minValue, maxValue, warningThreshold, dangerThreshold, label) {
    var ctx = document.getElementById(canvasId).getContext('2d');
    
    // 确定颜色
    var color;
    if (value < dangerThreshold) {
        color = '#F5222D'; // 危险 - 红色
    } else if (value < warningThreshold) {
        color = '#FAAD14'; // 警告 - 黄色
    } else {
        color = '#52C41A'; // 正常 - 绿色
    }
    
    var gaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, maxValue - value],
                backgroundColor: [color, '#F0F0F0'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            circumference: 180,
            rotation: 270,
            cutout: '75%',
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                animateRotate: true,
                animateScale: false,
                duration: 1000,
                easing: 'easeOutQuart'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        title: function() {
                            return label;
                        },
                        label: function(context) {
                            return '当前值: ' + value + ' / ' + maxValue;
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                intersect: false
            }
        },
        plugins: [{
            id: 'centerText',
            beforeDraw: function(chart) {
                var width = chart.width;
                var height = chart.height;
                var ctx = chart.ctx;
                
                ctx.restore();
                var fontSize = (height / 114).toFixed(2);
                ctx.font = "bold " + fontSize + "em sans-serif";
                ctx.textBaseline = "middle";
                ctx.fillStyle = color;
                
                var text = value;
                var textX = Math.round((width - ctx.measureText(text).width) / 2);
                var textY = height / 2 + 10;
                
                ctx.fillText(text, textX, textY);
                
                // 添加标签
                ctx.font = (fontSize * 0.6) + "em sans-serif";
                ctx.fillStyle = '#666';
                var labelX = Math.round((width - ctx.measureText(label).width) / 2);
                var labelY = height / 2 + 30;
                
                ctx.fillText(label, labelY, labelY);
                ctx.save();
            }
        }]
    });
    
    return gaugeChart;
}

// 创建趋势图
function createTrendChart(canvasId, data, label, color) {
    var ctx = document.getElementById(canvasId).getContext('2d');
    
    // 创建渐变背景
    var gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, color + '40');
    gradient.addColorStop(1, color + '00');
    
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => {
                var date = new Date(item.timestamp);
                return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            }),
            datasets: [{
                label: label,
                data: data.map(item => item.value),
                borderColor: color,
                backgroundColor: gradient,
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: color,
                pointHoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        maxTicksLimit: 8,
                        color: '#666'
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return '时间: ' + context[0].label;
                        },
                        label: function(context) {
                            return label + ': ' + context.parsed.y;
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    
    return chart;
}

// 创建塘口对比图表
function createPondComparisonChart() {
    var ctx = document.getElementById('pond-comparison').getContext('2d');
    
    // 生成模拟数据
    var pondNames = ['1号塘', '2号塘', '3号塘', '4号塘', '5号塘'];
    var dissolvedOxygen = [6.2, 5.8, 7.1, 4.9, 6.5];
    var temperature = [26.5, 27.2, 25.8, 26.9, 26.3];
    var ph = [7.8, 7.6, 8.1, 7.5, 7.9];
    
    var chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: pondNames,
            datasets: [
                {
                    label: '溶解氧 (mg/L)',
                    data: dissolvedOxygen,
                    backgroundColor: 'rgba(24, 144, 255, 0.6)',
                    borderColor: 'rgba(24, 144, 255, 1)',
                    borderWidth: 1
                },
                {
                    label: '温度 (°C)',
                    data: temperature,
                    backgroundColor: 'rgba(250, 173, 20, 0.6)',
                    borderColor: 'rgba(250, 173, 20, 1)',
                    borderWidth: 1
                },
                {
                    label: 'pH值',
                    data: ph,
                    backgroundColor: 'rgba(82, 196, 26, 0.6)',
                    borderColor: 'rgba(82, 196, 26, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        color: '#666',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return context[0].label + ' 水质数据';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    
    return chart;
}

// 创建参数对比图表
function createParameterComparisonChart() {
    var ctx = document.getElementById('parameter-comparison').getContext('2d');
    
    // 生成模拟数据 - 过去7天的数据
    var labels = [];
    var dissolvedOxygenData = [];
    var temperatureData = [];
    var phData = [];
    
    for (var i = 6; i >= 0; i--) {
        var date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }));
        
        dissolvedOxygenData.push((5.5 + Math.random() * 2).toFixed(1));
        temperatureData.push((25 + Math.random() * 3).toFixed(1));
        phData.push((7.5 + Math.random() * 0.8).toFixed(1));
    }
    
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '溶解氧 (mg/L)',
                    data: dissolvedOxygenData,
                    borderColor: '#1890FF',
                    backgroundColor: 'rgba(24, 144, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: '温度 (°C)',
                    data: temperatureData,
                    borderColor: '#FAAD14',
                    backgroundColor: 'rgba(250, 173, 20, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'pH值',
                    data: phData,
                    borderColor: '#52C41A',
                    backgroundColor: 'rgba(82, 196, 26, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        color: '#666',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return '日期: ' + context[0].label;
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    
    return chart;
}

// 创建预测图表
function createPredictionChart() {
    var ctx = document.getElementById('prediction-chart').getContext('2d');
    
    // 生成模拟数据 - 过去7天 + 未来3天的预测
    var labels = [];
    var actualData = [];
    var predictionData = [];
    
    // 过去7天的实际数据
    for (var i = 6; i >= 0; i--) {
        var date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }));
        actualData.push((5.5 + Math.random() * 2).toFixed(1));
        predictionData.push(null); // 过去数据没有预测值
    }
    
    // 未来3天的预测数据
    for (var i = 1; i <= 3; i++) {
        var date = new Date();
        date.setDate(date.getDate() + i);
        labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) + '(预测)');
        
        // 基于最后一天的实际值生成预测
        var lastActual = parseFloat(actualData[actualData.length - 1]);
        var trend = (Math.random() - 0.5) * 0.5; // 随机趋势
        predictionData.push((lastActual + trend).toFixed(1));
        actualData.push(null); // 未来数据没有实际值
    }
    
    var chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '实际溶解氧',
                    data: actualData,
                    borderColor: '#1890FF',
                    backgroundColor: 'rgba(24, 144, 255, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    spanGaps: false
                },
                {
                    label: '预测溶解氧',
                    data: predictionData,
                    borderColor: '#722ED1',
                    backgroundColor: 'rgba(114, 46, 209, 0.1)',
                    borderWidth: 3,
                    borderDash: [5, 5], // 虚线表示预测
                    fill: false,
                    tension: 0.3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    spanGaps: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#666',
                        padding: 10
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        color: '#666',
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        title: function(context) {
                            return '日期: ' + context[0].label;
                        },
                        label: function(context) {
                            if (context.parsed.y === null) {
                                return null;
                            }
                            return context.dataset.label + ': ' + context.parsed.y + ' mg/L';
                        }
                    }
                },
                annotation: {
                    annotations: {
                        line1: {
                            type: 'line',
                            xMin: 6.5,
                            xMax: 6.5,
                            borderColor: 'rgba(0, 0, 0, 0.3)',
                            borderWidth: 2,
                            borderDash: [6, 6],
                            label: {
                                content: '预测开始',
                                enabled: true,
                                position: 'top'
                            }
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
    
    return chart;
}

// 显示提示消息
function showToast(message, type = 'info', duration = 3000) {
    var toastId = 'toast-' + Date.now();
    var bgClass = type === 'success' ? 'bg-success' : (type === 'error' ? 'bg-danger' : 'bg-info');
    var icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle');
    
    var toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas ${icon} me-2"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // 确保容器存在
    if ($('#toast-container').length === 0) {
        $('body').append('<div id="toast-container" class="position-fixed bottom-0 end-0 p-3" style="z-index: 1050"></div>');
    }
    
    var toastElement = $(toastHtml);
    $('#toast-container').append(toastElement);
    
    var toast = new bootstrap.Toast(toastElement[0], {
        delay: duration
    });
    toast.show();
    
    // 自动移除toast元素
    toastElement.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// 获取投喂决策
function getFeedingDecision(pondId) {
    // 显示加载状态
    $('#decision-result').html('<div class="text-center"><div class="loading"></div> 正在分析数据...</div>');
    
    $.get('/decision/get_feeding_decision/' + pondId, function(data) {
        if (data.error) {
            $('#decision-result').html('<div class="alert alert-danger">' + data.error + '</div>');
            return;
        }
        
        var decisionHtml = `
            <div class="decision-card">
                <h3>${data.pond.name} - ${data.pond.species}</h3>
                <div class="decision-result">建议投喂量：${data.recommended_amount} kg</div>
                <div class="decision-reasoning">
                    <h5>决策依据：</h5>
                    <p>${data.reasoning}</p>
                </div>
                <div class="decision-actions mt-3">
                    <button class="btn btn-light" onclick="applyFeedingDecision(${data.decision_id})">
                        <i class="fas fa-check me-1"></i>应用此决策
                    </button>
                    <button class="btn btn-outline-light ms-2" onclick="showDecisionDetails(${data.decision_id})">
                        <i class="fas fa-info-circle me-1"></i>查看详情
                    </button>
                </div>
            </div>
        `;
        
        // 添加其他建议
        if (data.other_suggestions && data.other_suggestions.length > 0) {
            decisionHtml += '<div class="mt-3"><h5>其他建议：</h5>';
            data.other_suggestions.forEach(function(suggestion) {
                var alertClass = suggestion.type === 'oxygen' ? 'warning' : 'info';
                decisionHtml += `
                    <div class="alert alert-${alertClass} alert-dismissible fade show" role="alert">
                        <strong>${suggestion.title}：</strong>${suggestion.message}
                    </div>
                `;
            });
            decisionHtml += '</div>';
        }
        
        $('#decision-result').html(decisionHtml);
    }).fail(function() {
        $('#decision-result').html('<div class="alert alert-danger">获取决策失败，请稍后再试</div>');
    });
}

// 应用投喂决策
function applyFeedingDecision(decisionId) {
    $.post('/decision/apply_feeding_decision/' + decisionId, function(data) {
        if (data.success) {
            showToast(data.message, 'success');
            // 刷新投喂记录
            setTimeout(function() {
                location.reload();
            }, 1000);
        } else {
            showToast('应用决策失败', 'error');
        }
    });
}

// 显示决策详情
function showDecisionDetails(decisionId) {
    // 这里可以打开一个模态框显示更详细的决策信息
    $('#decisionDetailsModal').modal('show');
}

// 解决预警
function resolveAlert(alertId) {
    $.post('/alert/resolve/' + alertId, function(data) {
        if (data.success) {
            showToast(data.message, 'success');
            // 移除预警元素
            $('#alert-' + alertId).fadeOut();
        } else {
            showToast('操作失败', 'error');
        }
    });
}