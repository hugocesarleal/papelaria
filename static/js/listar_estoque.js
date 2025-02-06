document.getElementById("closeForm").onclick = function() {
    document.getElementById("formContainer").style.display = "none";
};

if (document.cookie.indexOf("email_cadastrado=true") !== -1) {
    document.getElementById("formContainer").style.display = "none";
}

function filtrarItens() {
    var input = document.getElementById('searchInput');
    var filter = input.value.toLowerCase();
    var cards = document.querySelectorAll('.card');
    
    cards.forEach(function(card) {
        var cardTitle = card.querySelector('.card-title');
        if (cardTitle) {
            var textValue = cardTitle.textContent || cardTitle.innerText;
            if (textValue.toLowerCase().indexOf(filter) > -1) {
                card.parentElement.style.display = ''; // Exibe o card
            } else {
                card.parentElement.style.display = 'none'; // Oculta o card
            }
        }
    });
}

document.getElementById("chatInput").addEventListener("input", function() {
    const chatMessages = document.getElementById("chatMessages");
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

document.getElementById("chatToggle").onclick = function() {
    const chatContainer = document.getElementById("chatContainer");
    chatContainer.style.display = "flex";
    setTimeout(() => {
        chatContainer.classList.add("open");
    }, 10); // Pequeno atraso para permitir a transição
    document.getElementById("chatToggle").style.display = "none";

    // Verifica se há mensagens no contêiner de mensagens do chat
    const chatMessages = document.getElementById("chatMessages");
    if (chatMessages.children.length === 0) {
        // Adiciona a mensagem inicial após a animação do chat
        setTimeout(() => {
            addMessage('bot', 'Olá! 😊 Sou o assistente virtual da papelaria do DCE. Como posso te ajudar hoje? Se precisar de algo que eu não souber responder, posso encaminhar sua dúvida para nossos administradores!');
        }, 300); // Tempo da transição
    }
};

document.getElementById("closeChat").onclick = function() {
    const chatContainer = document.getElementById("chatContainer");
    chatContainer.classList.remove("open");
    setTimeout(() => {
        chatContainer.style.display = "none";
        document.getElementById("chatToggle").style.display = "flex";
    }, 300); // Tempo da transição
};

let typingTimeout; // Variável global para rastrear o timeout da animação de digitação
let isTyping = false; // Variável global para rastrear se o bot está digitando

function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (message) {
        if (isTyping) {
            clearTimeout(typingTimeout); // Limpa o timeout anterior
            isTyping = false; // Reseta o estado de digitação
        }

        const sendButton = document.getElementById('sendButton');
        sendButton.classList.add('animate');
        setTimeout(() => {
            sendButton.classList.remove('animate');
        }, 300);

        addMessage('user', message);
        input.value = '';

        // Adiciona um atraso antes de enviar a mensagem para o backend

        // Enviar mensagem para o backend
        fetch("{% url 'chatbot' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response) {
                setTimeout(() => {
                    addMessage('bot', data.response);
                }, 1000); // Delay de 1 segundo (1000 milissegundos)
            } else {
                setTimeout(() => {
                    addFormMessage();
                }, 1000); // Delay de 1 segundo (1000 milissegundos)
            }
        });
    }
}

function sendEmail() {
    const name = document.getElementById('userName').value.trim();
    const email = document.getElementById('userEmail').value.trim();
    const message = document.getElementById('userMessage').value.trim();
    if (name && email && message) {
        fetch("{% url 'save_question' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({ name: name, email: email, message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addMessage('bot', 'Sua dúvida foi encaminhada para o administrador. Você receberá uma resposta em breve.');
                document.getElementById('emailForm').style.display = 'none';
                const formMessage = document.querySelector('.message.form');
                if (formMessage) {
                    formMessage.remove();
                }
            } else {
                console.error('Erro ao enviar dúvida:', data.error);
            }
        })
        .catch(error => {
            console.error('Erro ao enviar dúvida:', error);
        });
    } else {
        console.error('Preencha todos os campos do formulário.');
    }
}

function addMessage(sender, message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    // Calcular largura do balão de mensagem com base na quantidade de caracteres
    const charCount = message.length;
    const minWidth = 50; // largura mínima em pixels
    const maxWidth = 800; // largura máxima em pixels
    const charWidth = 12; // largura média de um caractere em pixels
    const calculatedWidth = Math.min(maxWidth, Math.max(minWidth, charCount * charWidth));
    messageDiv.style.width = calculatedWidth + 'px';
    messageDiv.style.whiteSpace = 'normal';
    messageDiv.style.wordWrap = 'break-word';

    chatMessages.appendChild(messageDiv);
    if (sender === 'bot') {
        typeMessage(messageDiv, message);
    } else {
        messageDiv.textContent = message;
    }
    messageDiv.scrollIntoView({ behavior: 'smooth' });

    // Reproduzir áudio apenas quando sender for 'bot'
    if (sender === 'bot') {
        const audio = new Audio('/static/mp3/chat.mp3');
        audio.volume = 0.2; // Define o volume para 20%
        audio.play();
    }
}

function addFormMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const formDiv = document.createElement('div');
    formDiv.classList.add('message', 'form');
    formDiv.innerHTML = `
        <div class="email-form" id="emailForm">
            <input type="text" id="userName" placeholder="Digite seu nome..." required>
            <input type="email" id="userEmail" placeholder="Digite seu email..." required>
            <textarea id="userMessage" placeholder="Detalhe sua dúvida..." required style="overflow: hidden; resize: none;"></textarea>
            <button onclick="sendEmail()">Enviar</button>
        </div>
    `;
    chatMessages.appendChild(formDiv);

    // Selecionar a textarea e adicionar evento de input para ajustar a altura
    const textarea = formDiv.querySelector('textarea');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    addMessage('bot', 'Descreva melhor sua dúvida, e em breve um de nossos administradores irá te responder.');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function typeMessage(element, message, index = 0) {
    if (index < message.length) {
        element.textContent += message.charAt(index);
        isTyping = true; // Define o estado de digitação como verdadeiro
        typingTimeout = setTimeout(() => typeMessage(element, message, index + 1), 30); // Ajuste o tempo conforme necessário
    } else {
        isTyping = false; // Reseta o estado de digitação quando a mensagem estiver completa
    }
}