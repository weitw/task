
var BaseFormValidation = function() {
    var initValidationBootstrap = function(){
        jQuery('.js-validation-bootstrap').validate({
            errorClass: 'help-block animated fadeInDown',
            errorElement: 'div',
            errorPlacement: function(error, e) {
                jQuery(e).parents('.form-group > div').append(error);
            },
            highlight: function(e) {
                jQuery(e).closest('.form-group').removeClass('has-error').addClass('has-error');
                jQuery(e).closest('.help-block').remove();
            },
            success: function(e) {
                jQuery(e).closest('.form-group').removeClass('has-error');
                jQuery(e).closest('.help-block').remove();
            },
            rules: {
                'username': {
                    required: true,
                    minlength: 3,
                    havename:true
                },
                'email': {
                    required: true,
                    email: true
                },
                'password': {
                    required: true,
                    minlength: 6
                },
                'confirm': {
                    required: true,
                    equalTo: '#password'
                },
                'password1': {
                    required: true,
                    minlength: 6
                },
                'confirm1': {
                    required: true,
                    equalTo: '#password1'
                },
                'password2': {
                    required: true,
                    minlength: 6
                },
                'confirm2': {
                    required: true,
                    equalTo: '#password2'
                },
                'status': {
                    required: true,
                },
                'val-suggestions': {
                    required: true,
                    minlength: 5
                },
                'val-skill': {
                    required: true
                },
                'val-website': {
                    required: true,
                    url: true
                },
                'val-digits': {
                    required: true,
                    digits: true
                },
                'val-number': {
                    required: true,
                    number: true
                },
                'val-range': {
                    required: true,
                    range: [1, 10]
                },
                'val-terms': {
                    required: true
                }
            },
            messages: {
                'username': {
                    required: '请输入用户名',
                    minlength: '用户名长度不少于3'
                },
                'email': '请输入邮箱地址',
                'password': {
                    required: '请输入密码',
                    minlength: '密码长度至少6位'
                },
                'confirm': {
                    required: '请输入确认密码',
                    minlength: '你的密码长度至少6位',
                    equalTo: '两次密码输入不一致!!!'
                },
                'status': {
                    required: '请选择身份',
                },
                'val-suggestions': 'What can we do to become better?',
                'val-skill': 'Please select a skill!',
                'val-website': 'Please enter your website!',
                'val-digits': 'Please enter only digits!',
                'val-number': 'Please enter a number!',
                'val-range': 'Please enter a number between 1 and 10!',
                'val-terms': 'You must agree to the service terms!'
            }
        });
    };   

    return {
        init: function () {
            // Init Bootstrap Forms Validation
            initValidationBootstrap();         
        }
    };
}();

// Initialize when page loads
jQuery(function(){ BaseFormValidation.init(); });