document.addEventListener('DOMContentLoaded', function() {
    console.log('错题猎手已加载');
    
    // 隐藏聊天相关的alert
    setTimeout(function() {
        const aiAlerts = document.querySelectorAll('.alert');
        aiAlerts.forEach(alert => {
            if (alert.textContent.includes('AI: 这是对您问题') || alert.textContent.includes('用户:')) {
                alert.style.display = 'none';
            }
        });
    }, 100);
});
