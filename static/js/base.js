$('#btnEsqueciSenha').click(function() {
    toastr.info('Se você esqueceu sua senha, contate o administrador do sistema!.', 'Informação');
  });

document.addEventListener("DOMContentLoaded", function() {
  const sidebar = document.getElementById("sidebar");

  // Expande a sidebar ao passar o mouse
  sidebar.addEventListener("mouseover", function() {
    sidebar.classList.remove("active");
  });

  // Recolhe a sidebar ao remover o mouse
  sidebar.addEventListener("mouseout", function() {
    sidebar.classList.add("active");
  });
});
$(document).ready(function() {
  $("#sidebarCollapse").on("click", function() {
    $("#sidebar").toggleClass("active");
  });
});

  document.querySelectorAll('.nav-group-toggle').forEach((toggle) => {
      toggle.addEventListener('click', (e) => {
          e.preventDefault();
          const parent = toggle.parentElement;
          parent.classList.toggle('show');
          const groupItems = parent.querySelector('.nav-group-items');
          if (groupItems) {
              groupItems.classList.toggle('show');
          }
      });
  });
  
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

      
  });


    document.getElementById('togglePassword').addEventListener('click', function (e) {
        const passwordInput = document.getElementById('password');
        const icon = this.querySelector('i');
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            passwordInput.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    });