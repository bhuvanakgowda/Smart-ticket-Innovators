// Smart Bus Ticket System Chatbot
class BusChatbot {
    constructor() {
        this.isOpen = false;
        this.messages = [];
        this.knowledgeBase = this.initKnowledgeBase();
    }

    initKnowledgeBase() {
        return {
            'hello': 'Hello! How can I help you today? I can assist with:\n• Bus routes and schedules\n• Ticket booking\n• Wallet balance\n• Fare information\n• How to scan QR/Face',
            'hi': 'Hello! How can I help you today? I can assist with:\n• Bus routes and schedules\n• Ticket booking\n• Wallet balance\n• Fare information\n• How to scan QR/Face',
            'hey': 'Hello! How can I help you today?',
            'help': 'I can help you with:\n\n📍 **Bus Routes** - Information about available routes\n🎫 **Tickets** - How to book and scan tickets\n💳 **Wallet** - Check balance and recharge\n💰 **Fare** - Calculate and view fares\n📱 **QR Code** - How to scan QR codes\n👤 **Face Recognition** - How to use face scan\n❓ **FAQ** - Common questions',
            'route': 'Here are our bus routes:\n\n🚌 **BUS101**: City Center → Airport\n   Fare: ₹37.5 | Distance: 15km\n\n🚌 **BUS202**: Central Station → Mall\n   Fare: ₹20 | Distance: 10km\n\n🚌 **BUS303**: University → Tech Park\n   Fare: ₹60 | Distance: 20km',
            'routes': 'Here are our bus routes:\n\n🚌 **BUS101**: City Center → Airport\n   Fare: ₹37.5 | Distance: 15km\n\n🚌 **BUS202**: Central Station → Mall\n   Fare: ₹20 | Distance: 10km\n\n🚌 **BUS303**: University → Tech Park\n   Fare: ₹60 | Distance: 20km',
            'bus': 'Here are our bus routes:\n\n🚌 **BUS101**: City Center → Airport\n   Fare: ₹37.5 | Distance: 15km\n\n🚌 **BUS202**: Central Station → Mall\n   Fare: ₹20 | Distance: 10km\n\n🚌 **BUS303**: University → Tech Park\n   Fare: ₹60 | Distance: 20km',
            'ticket': 'To book a ticket:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Scan QR code or use Face Recognition\n4. Ticket is generated automatically!\n\nYour wallet will be charged automatically.',
            'tickets': 'To book a ticket:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Scan QR code or use Face Recognition\n4. Ticket is generated automatically!\n\nYour wallet will be charged automatically.',
            'book': 'To book a ticket:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Scan QR code or use Face Recognition\n4. Ticket is generated automatically!',
            'wallet': 'Wallet Features:\n\n💰 Check your balance\n💳 Recharge with any amount\n📜 View transaction history\n\nGo to **Wallet** page to manage your wallet.',
            'balance': 'To check your wallet balance:\n\n1. Go to **Wallet** page\n2. Select your profile\n3. View your current balance\n\nYou can also see balance after each ticket purchase.',
            'fare': 'Our fare is calculated based on distance:\n\n💰 ₹2.5 per km for standard buses\n💰 ₹2.0 per km for express buses\n\nExample: 15km journey = ₹37.5',
            'price': 'Our fare is calculated based on distance:\n\n💰 ₹2.5 per km for standard buses\n💰 ₹2.0 per km for express buses\n\nExample: 15km journey = ₹37.5',
            'cost': 'Our fare is calculated based on distance:\n\n💰 ₹2.5 per km for standard buses\n💰 ₹2.0 per km for express buses\n\nExample: 15km journey = ₹37.5',
            'qr': 'To scan QR Code:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Enter QR Code (e.g., QR001)\n4. Click "Scan QR"\n\nAvailable QR Codes: QR001, QR002, QR003, QR004',
            'qr code': 'To scan QR Code:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Enter QR Code (e.g., QR001)\n4. Click "Scan QR"\n\nAvailable QR Codes: QR001, QR002, QR003, QR004',
            'scan': 'Scanning options:\n\n📱 **QR Code**: Enter your QR code number\n👤 **Face Recognition**: Use camera to scan face\n\nGo to **Scan Passenger** page to try!',
            'face': 'To use Face Recognition:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Click "Start Camera"\n4. Allow camera permissions\n5. Position your face in frame\n6. Click "Capture & Scan"\n\nAvailable Face IDs: FACE001, FACE002, FACE003, FACE004',
            'face recognition': 'To use Face Recognition:\n\n1. Go to **Scan Passenger** page\n2. Select your bus\n3. Click "Start Camera"\n4. Allow camera permissions\n5. Position your face in frame\n6. Click "Capture & Scan"',
            'admin': 'Admin Dashboard provides:\n\n📊 Real-time statistics\n👥 Passenger count\n💰 Revenue tracking\n🚌 Bus management\n📜 Recent tickets\n\nGo to **Admin** page to view!',
            'dashboard': 'Admin Dashboard provides:\n\n📊 Real-time statistics\n👥 Passenger count\n💰 Revenue tracking\n🚌 Bus management\n📜 Recent tickets\n\nGo to **Admin** page to view!',
            'recharge': 'To recharge your wallet:\n\n1. Go to **Wallet** page\n2. Select your profile\n3. Click "Recharge Wallet"\n4. Enter amount or use quick amounts\n5. Click "Recharge Now"\n\nQuick amounts: ₹100, ₹250, ₹500, ₹1000',
            'recharge wallet': 'To recharge your wallet:\n\n1. Go to **Wallet** page\n2. Select your profile\n3. Click "Recharge Wallet"\n4. Enter amount or use quick amounts\n5. Click "Recharge Now"',
            'thank': 'You\'re welcome! 😊\n\nIs there anything else I can help you with?',
            'thanks': 'You\'re welcome! 😊\n\nIs there anything else I can help you with?',
            'thank you': 'You\'re welcome! 😊\n\nIs there anything else I can help you with?',
            'bye': 'Goodbye! 👋\n\nThank you for using Smart Bus Ticket System!\nHave a safe journey!',
            'goodbye': 'Goodbye! 👋\n\nThank you for using Smart Bus Ticket System!',
            'how are you': 'I\'m doing great! Thank you for asking 😊\n\nHow can I assist you today?',
            'what': 'I\'m your Smart Bus Assistant!\n\nI can help you with:\n• Bus routes and schedules\n• Ticket booking process\n• Wallet management\n• Fare information\n• How to use QR/Face scan',
            'who': 'I\'m your Smart Bus Assistant!\n\nI\'m here to help you with the bus ticket system. Just ask me anything!',
            'system': 'Smart Bus Ticket System Features:\n\n📱 QR Code Scanning\n👤 Face Recognition\n💳 Digital Wallet\n🎫 Instant Tickets\n🔒 Duplicate Prevention\n📊 Admin Dashboard',
            'features': 'Smart Bus Ticket System Features:\n\n📱 QR Code Scanning\n👤 Face Recognition\n💳 Digital Wallet\n🎫 Instant Tickets\n🔒 Duplicate Prevention\n📊 Admin Dashboard',
            'contact': 'For additional support:\n\n📧 Email: support@smartbus.com\n📞 Phone: 1800-BUS-HELP\n\nOr ask me any question!',
            'support': 'For support:\n\n📧 Email: support@smartbus.com\n📞 Phone: 1800-BUS-HELP\n\nOr ask me any question!',
            'faq': 'Frequently Asked Questions:\n\n**Q: How do I get a ticket?**\nA: Scan QR code or use Face Recognition\n\n**Q: How is fare calculated?**\nA: Based on distance (₹2-3 per km)\n\n**Q: Can I recharge wallet?**\nA: Yes, go to Wallet page\n\n**Q: Is face scan secure?**\nA: Yes, it uses your unique Face ID'
        };
    }

    getResponse(input) {
        const message = input.toLowerCase().trim();
        
        // Check for exact matches first
        if (this.knowledgeBase[message]) {
            return this.knowledgeBase[message];
        }
        
        // Check for partial matches
        for (const [key, value] of Object.entries(this.knowledgeBase)) {
            if (message.includes(key)) {
                return value;
            }
        }
        
        // Default response
        return 'I\'m not sure I understand that. 😕\n\nTry asking about:\n• Bus routes\n• Ticket booking\n• Wallet\n• QR scanning\n• Face recognition\n\nOr type "help" for more options!';
    }

    addMessage(text, sender) {
        this.messages.push({ text, sender, time: new Date() });
    }

    renderMessages() {
        const container = document.getElementById('chatbot-messages');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message ${msg.sender}`;
            messageDiv.innerHTML = `
                <div class="message-content">${msg.text.replace(/\n/g, '<br>')}</div>
                <div class="message-time">${msg.time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
            `;
            container.appendChild(messageDiv);
        });
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    toggle() {
        const chatbot = document.getElementById('chatbot');
        const toggleBtn = document.getElementById('chatbot-toggle');
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            chatbot.classList.add('open');
            toggleBtn.innerHTML = '✕';
            
            // Show welcome message if first time
            if (this.messages.length === 0) {
                this.addMessage('Hello! 👋\n\nI\'m your Smart Bus Assistant. How can I help you today?', 'bot');
                this.renderMessages();
            }
        } else {
            chatbot.classList.remove('open');
            toggleBtn.innerHTML = '💬';
        }
    }

    sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        this.renderMessages();
        
        // Clear input
        input.value = '';
        
        // Get bot response after a short delay
        setTimeout(() => {
            const response = this.getResponse(message);
            this.addMessage(response, 'bot');
            this.renderMessages();
        }, 500);
    }
}

// Initialize chatbot
let chatbot;

function initChatbot() {
    chatbot = new BusChatbot();
    
    // Set up event listeners
    document.getElementById('chatbot-toggle').addEventListener('click', () => {
        chatbot.toggle();
    });
    
    document.getElementById('chatbot-send').addEventListener('click', () => {
        chatbot.sendMessage();
    });
    
    document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            chatbot.sendMessage();
        }
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initChatbot);

