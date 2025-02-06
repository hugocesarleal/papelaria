function handleUserClick() {
    const dropdown = document.getElementById("dropdown-menu");
    dropdown.classList.toggle("show");
}

$(document).ready(function () {
    toastr.options = {
        "closeButton": true,
        "debug": false,
        "newestOnTop": true,
        "progressBar": true,
        "positionClass": "toast-top-right",
        "preventDuplicates": false,
        "onclick": null,
        "showDuration": "300",
        "hideDuration": "1000",
        "timeOut": "5000",
        "extendedTimeOut": "1000",
        "showEasing": "swing",
        "hideEasing": "linear",
        "showMethod": "fadeIn",
        "hideMethod": "fadeOut"
    };

    $(document).ready(function() {
        $('#btnEsqueciSenha').click(function() {
            toastr.info('Se você esqueceu sua senha, contate o administrador do sistema!', 'Informação');
          });
    });
});