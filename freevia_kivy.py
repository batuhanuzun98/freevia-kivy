import sys
import threading
import urllib.parse
import os
try:
    from plyer import gps
except ImportError:
    gps = None
try:
    from PIL import Image, ImageDraw
except ImportError:
    print("PIL kütüphanesi bulunamadı. 'pip install Pillow' ile yükleyin.")
    Image = None
    ImageDraw = None
import requests

# Cross-platform geolocation function
def get_user_location(callback=None):
    """
    Attempts to get the user's location:
    - On Android/iOS: uses Plyer GPS (calls callback with (lat, lon)).
    - On desktop: uses IP-based geolocation (returns (lat, lon)).
    If callback is provided, calls it with the result (async for mobile).
    """
    platform = sys.platform
    if platform in ("android", "ios") and gps is not None:
        # Mobile: use Plyer GPS
        def on_location(**kwargs):
            lat = kwargs.get('lat')
            lon = kwargs.get('lon')
            if lat is not None and lon is not None:
                print(f"GPS Location found: {lat}, {lon}")
                if callback:
                    callback((lat, lon))
            else:
                print("GPS Location data incomplete")
                if callback:
                    callback(None)

        def on_status(status_type, status):
            print(f"GPS Status: {status_type} - {status}")
            if status_type == 'provider-disabled':
                print("GPS is disabled. Please enable GPS in settings.")
                if callback:
                    callback(None)

        try:
            # Request location permissions
            print("Requesting GPS location...")
            gps.configure(on_location=on_location, on_status=on_status)
            gps.start(minTime=1000, minDistance=1)
        except NotImplementedError:
            print("GPS not available on this platform")
            if callback:
                callback(None)
        except Exception as e:
            print(f"GPS Error: {e}")
            if callback:
                callback(None)
    else:
        # Desktop: use multiple IP-based geolocation services for better accuracy
        def fetch_ip_location():
            print("Fetching location from IP...")
            services = [
                ('https://ipapi.co/json/', lambda d: (d.get('latitude'), d.get('longitude'))),
                ('http://ip-api.com/json/', lambda d: (d.get('lat'), d.get('lon'))),
                ('https://ipinfo.io/json', lambda d: tuple(map(float, d.get('loc', '').split(','))) if d.get('loc') else (None, None)),
                ('https://geolocation-db.com/json/', lambda d: (d.get('latitude'), d.get('longitude')))
            ]
            
            for service_url, parser in services:
                try:
                    print(f"Trying service: {service_url}")
                    headers = {'User-Agent': 'FreeviaApp/1.0'}
                    resp = requests.get(service_url, timeout=10, headers=headers)
                    data = resp.json()
                    lat, lon = parser(data)
                    
                    if lat is not None and lon is not None:
                        result = (float(lat), float(lon))
                        print(f"IP Location found via {service_url}: {lat}, {lon}")
                        break
                    else:
                        print(f"No valid location data from {service_url}")
                except Exception as e:
                    print(f"Error with {service_url}: {e}")
                    continue
            else:
                result = None
                print("All IP location services failed")
            
            if callback:
                callback(result)
            else:
                return result
        # Run in thread to avoid blocking UI
        if callback:
            threading.Thread(target=fetch_ip_location).start()
        else:
            return fetch_ip_location()

def create_blue_pin():
    """Create a blue pin marker for user location"""
    if Image is None or ImageDraw is None:
        print("PIL not available, cannot create blue pin")
        return None
    
    # Create a blue pin marker (64x64 pixels)
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Pin colors (iOS blue)
    pin_color = (0, 122, 255, 255)  # iOS blue
    border_color = (255, 255, 255, 255)  # White border
    
    # Draw pin shape
    center_x, center_y = size // 2, size // 2 - 8
    pin_radius = 18
    
    # Pin circle with white border
    draw.ellipse([center_x - pin_radius - 2, center_y - pin_radius - 2, 
                  center_x + pin_radius + 2, center_y + pin_radius + 2], 
                 fill=border_color)
    draw.ellipse([center_x - pin_radius, center_y - pin_radius, 
                  center_x + pin_radius, center_y + pin_radius], 
                 fill=pin_color)
    
    # Pin point
    point_width = 8
    point_height = 16
    draw.polygon([
        (center_x, center_y + pin_radius),
        (center_x - point_width, center_y + pin_radius + point_height),
        (center_x + point_width, center_y + pin_radius + point_height)
    ], fill=pin_color)
    
    # Inner dot
    dot_radius = 6
    draw.ellipse([center_x - dot_radius, center_y - dot_radius, 
                  center_x + dot_radius, center_y + dot_radius], 
                 fill=(255, 255, 255, 255))
    
    return img

def ensure_blue_pin_exists():
    """Ensure blue pin image exists, create if not"""
    blue_pin_path = get_data_file_path('blue_pin.png')
    if not os.path.exists(blue_pin_path):
        try:
            pin = create_blue_pin()
            if pin:
                pin.save(blue_pin_path)
                print(f"Blue pin marker created: {blue_pin_path}")
                return blue_pin_path
        except Exception as e:
            print(f"Could not create blue pin: {e}")
            return None
    return blue_pin_path

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.animation import Animation

# iOS-style color palette
IOS_COLORS = {
    'primary_blue': get_color_from_hex('#007AFF'),
    'background': get_color_from_hex('#F2F2F7'),
    'card_background': get_color_from_hex('#FFFFFF'),
    'text_primary': get_color_from_hex('#000000'),
    'text_secondary': get_color_from_hex('#8E8E93'),
    'text_tertiary': get_color_from_hex('#C7C7CC'),
    'border': get_color_from_hex('#C6C6C8'),
    'separator': get_color_from_hex('#C6C6C8'),
    'success': get_color_from_hex('#34C759'),
    'warning': get_color_from_hex('#FF9500'),
    'error': get_color_from_hex('#FF3B30'),
    'destructive': get_color_from_hex('#FF3B30'),
    'tint': get_color_from_hex('#007AFF')
}

import csv
import os
from kivy_garden.mapview import MapView, MapMarker

# Cross-platform file path handling
def get_app_data_dir():
    """Get the appropriate data directory for the current platform"""
    if sys.platform == "ios":
        # iOS: Use Documents directory
        from kivy.utils import platform
        if platform == "ios":
            import os
            return os.path.expanduser('~/Documents')
    elif sys.platform == "android":
        # Android: Use external storage
        from kivy.utils import platform
        if platform == "android":
            from android.storage import primary_external_storage_path
            return primary_external_storage_path()
    
    # Desktop: Use current directory
    return os.getcwd()

def get_data_file_path(filename):
    """Get the full path for a data file"""
    data_dir = get_app_data_dir()
    return os.path.join(data_dir, filename)

USERS_FILE = get_data_file_path('users.csv')

# Custom iOS-style components
class IOSButton(Button):
    def __init__(self, **kwargs):
        # Extract button_type from kwargs
        self.button_type = kwargs.pop('button_type', 'primary')
        super().__init__(**kwargs)
        
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.font_size = dp(17)
        self.font_name = 'Roboto'
        self.bold = True
        self.size_hint_y = None
        self.height = dp(50)
        
        # Set colors based on button type
        if self.button_type == 'destructive':
            self.bg_color = IOS_COLORS['destructive']
            self.text_color = [1, 1, 1, 1]  # White text
        else:
            self.bg_color = IOS_COLORS['primary_blue']
            self.text_color = [1, 1, 1, 1]  # White text
        
        self.color = self.text_color
        
        with self.canvas.before:
            Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(13)])
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        self.bind(on_press=self.on_button_press)
    
    def on_button_press(self, instance):
        # iOS-style button press animation
        anim = Animation(opacity=0.6, duration=0.1) + Animation(opacity=1.0, duration=0.1)
        anim.start(self)
    
    def update_graphics(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

class IOSSecondaryButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.font_size = dp(17)
        self.font_name = 'Roboto'
        self.color = IOS_COLORS['primary_blue']
        self.size_hint_y = None
        self.height = dp(50)
        
        with self.canvas.before:
            Color(*IOS_COLORS['separator'])
            self.border_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(13)])
            Color(*IOS_COLORS['card_background'])
            self.bg_rect = RoundedRectangle(size=(self.width-dp(1), self.height-dp(1)), 
                                         pos=(self.x+dp(0.5), self.y+dp(0.5)), radius=[dp(12.5)])
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        self.border_rect.size = self.size
        self.border_rect.pos = self.pos
        self.bg_rect.size = (self.width-dp(1), self.height-dp(1))
        self.bg_rect.pos = (self.x+dp(0.5), self.y+dp(0.5))

class IOSTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # iOS-style input field with visible text
        self.background_normal = ''
        self.background_active = ''
        self.background_color = [1, 1, 1, 1]  # White background
        self.foreground_color = [0, 0, 0, 1]  # Black text
        self.hint_text_color = [0.56, 0.56, 0.58, 1]  # iOS secondary text color
        self.cursor_color = [0, 0.48, 1, 1]  # iOS blue cursor
        self.selection_color = [0, 0.48, 1, 0.3]  # iOS blue selection
        self.font_size = dp(17)
        self.size_hint_y = None
        self.height = dp(50)
        self.padding = [dp(16), dp(15)]
        
        # Simple border styling that doesn't interfere with text
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.78, 0.78, 0.8, 1)  # iOS border color
            self.border_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = RoundedRectangle(size=(self.width-dp(2), self.height-dp(2)), 
                                         pos=(self.x+dp(1), self.y+dp(1)), radius=[dp(9)])
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        self.border_rect.size = self.size
        self.border_rect.pos = self.pos
        self.bg_rect.size = (self.width-dp(2), self.height-dp(2))
        self.bg_rect.pos = (self.x+dp(1), self.y+dp(1))

class IOSLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Roboto'
        self.color = IOS_COLORS['text_primary']

class IOSCard(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*IOS_COLORS['card_background'])
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(16)])
        
        self.bind(size=self.update_graphics, pos=self.update_graphics)
    
    def update_graphics(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

def save_user(username, password):
    with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([username, password])

def user_exists(username):
    if not os.path.exists(USERS_FILE):
        return False
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == username:
                return True
    return False

def check_user(username, password):
    if not os.path.exists(USERS_FILE):
        return False
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2 and row[0] == username and row[1] == password:
                return True
    return False

class SignInScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set background color
        with self.canvas.before:
            Color(*IOS_COLORS['background'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        # Main layout
        main_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        
        # Card container
        card_layout = BoxLayout(orientation='vertical', spacing=dp(20), 
                               size_hint=(None, None), size=(dp(320), dp(420)))
        
        # App title with iOS Large Title style
        title_label = IOSLabel(text='Freevia', font_size=dp(34), bold=True, 
                              size_hint_y=None, height=dp(60),
                              halign='center', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))
        card_layout.add_widget(title_label)
        
        # Subtitle
        subtitle_label = IOSLabel(text='Giriş Yap', font_size=dp(20), 
                                 color=IOS_COLORS['text_secondary'],
                                 size_hint_y=None, height=dp(30),
                                 halign='center')
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        card_layout.add_widget(subtitle_label)
        
        # Input fields - using simple TextInput with iOS colors for visibility
        self.username = TextInput(
            hint_text='Kullanıcı Adı', 
            multiline=False,
            size_hint_y=None, 
            height=dp(50),
            font_size=dp(17), 
            padding=[dp(16), dp(15)],
            background_color=[1, 1, 1, 1],  # White background
            foreground_color=[0, 0, 0, 1],  # Black text
            cursor_color=[0, 0.48, 1, 1]    # iOS blue cursor
        )
        self.password = TextInput(
            hint_text='Şifre', 
            password=True, 
            multiline=False,
            size_hint_y=None, 
            height=dp(50),
            font_size=dp(17), 
            padding=[dp(16), dp(15)],
            background_color=[1, 1, 1, 1],  # White background
            foreground_color=[0, 0, 0, 1],  # Black text
            cursor_color=[0, 0.48, 1, 1]    # iOS blue cursor
        )
        
        card_layout.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Spacer
        card_layout.add_widget(self.username)
        card_layout.add_widget(self.password)
        card_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))  # Spacer
        
        # Buttons
        btn_login = IOSButton(text='Giriş Yap')
        btn_login.bind(on_press=self.login)
        
        btn_signup = IOSSecondaryButton(text='Kayıt Ol')
        btn_signup.bind(on_press=self.goto_signup)
        
        card_layout.add_widget(btn_login)
        card_layout.add_widget(btn_signup)
        
        main_layout.add_widget(card_layout)
        self.add_widget(main_layout)
    
    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def login(self, instance):
        uname = self.username.text.strip()
        pwd = self.password.text.strip()
        
        if not uname or not pwd:
            self.show_ios_popup('Hata', 'Kullanıcı adı ve şifre gerekli!')
            return
            
        if check_user(uname, pwd):
            # Set user in dashboard and navigate there
            dashboard_screen = self.manager.get_screen('dashboard')
            dashboard_screen.set_user(uname)
            profile_screen = self.manager.get_screen('profile')
            profile_screen.set_user(uname)
            self.manager.current = 'dashboard'
        else:
            self.show_ios_popup('Hata', 'Kullanıcı adı veya şifre yanlış!')

    def goto_signup(self, instance):
        self.manager.current = 'signup'
    
    def show_ios_popup(self, title, message):
        """Show iOS-style popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Message label
        msg_label = IOSLabel(text=message, font_size=dp(16), 
                            color=IOS_COLORS['text_primary'], 
                            text_size=(dp(250), None), halign='center')
        content.add_widget(msg_label)
        
        # OK button
        ok_button = IOSButton(text='Tamam', size_hint_y=None, height=dp(44))
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                     background_color=IOS_COLORS['card_background'])
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()

class SignUpScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set background color
        with self.canvas.before:
            Color(*IOS_COLORS['background'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        # Main layout
        main_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        
        # Card container
        card_layout = BoxLayout(orientation='vertical', spacing=dp(20), 
                               size_hint=(None, None), size=(dp(320), dp(420)))
        
        # App title with iOS Large Title style
        title_label = IOSLabel(text='Freevia', font_size=dp(34), bold=True, 
                              size_hint_y=None, height=dp(60),
                              halign='center', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))
        card_layout.add_widget(title_label)
        
        # Subtitle
        subtitle_label = IOSLabel(text='Kayıt Ol', font_size=dp(20), 
                                 color=IOS_COLORS['text_secondary'],
                                 size_hint_y=None, height=dp(30),
                                 halign='center')
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        card_layout.add_widget(subtitle_label)
        
        # Input fields - using simple TextInput with iOS colors for visibility
        self.username = TextInput(
            hint_text='Kullanıcı Adı', 
            multiline=False,
            size_hint_y=None, 
            height=dp(50),
            font_size=dp(17), 
            padding=[dp(16), dp(15)],
            background_color=[1, 1, 1, 1],  # White background
            foreground_color=[0, 0, 0, 1],  # Black text
            cursor_color=[0, 0.48, 1, 1]    # iOS blue cursor
        )
        self.password = TextInput(
            hint_text='Şifre', 
            password=True, 
            multiline=False,
            size_hint_y=None, 
            height=dp(50),
            font_size=dp(17), 
            padding=[dp(16), dp(15)],
            background_color=[1, 1, 1, 1],  # White background
            foreground_color=[0, 0, 0, 1],  # Black text
            cursor_color=[0, 0.48, 1, 1]    # iOS blue cursor
        )
        
        card_layout.add_widget(Widget(size_hint_y=None, height=dp(10)))  # Spacer
        card_layout.add_widget(self.username)
        card_layout.add_widget(self.password)
        card_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))  # Spacer
        
        # Buttons
        btn_register = IOSButton(text='Kayıt Ol')
        btn_register.bind(on_press=self.register)
        
        btn_back = IOSSecondaryButton(text='Geri Dön')
        btn_back.bind(on_press=self.goto_signin)
        
        card_layout.add_widget(btn_register)
        card_layout.add_widget(btn_back)
        
        main_layout.add_widget(card_layout)
        self.add_widget(main_layout)
    
    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def register(self, instance):
        uname = self.username.text.strip()
        pwd = self.password.text.strip()
        if not uname or not pwd:
            self.show_ios_popup('Hata', 'Boş alan bırakmayınız!')
            return
        if user_exists(uname):
            self.show_ios_popup('Hata', 'Bu kullanıcı adı zaten var!')
            return
        save_user(uname, pwd)
        self.show_ios_popup('Başarılı', 'Kayıt başarılı!')
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'signin'), 1.5)

    def goto_signin(self, instance):
        self.manager.current = 'signin'
    
    def show_ios_popup(self, title, message):
        """Show iOS-style popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Message label
        msg_label = IOSLabel(text=message, font_size=dp(16), 
                            color=IOS_COLORS['text_primary'], 
                            text_size=(dp(250), None), halign='center')
        content.add_widget(msg_label)
        
        # OK button
        ok_button = IOSButton(text='Tamam', size_hint_y=None, height=dp(44))
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                     background_color=IOS_COLORS['card_background'])
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None  # Will store logged in username
        
        # Set background color
        with self.canvas.before:
            Color(*IOS_COLORS['background'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        # Main scroll layout for all content
        scroll = ScrollView()
        
        # Main content layout
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20), 
                               padding=[dp(20), dp(40), dp(20), dp(20)],
                               size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Welcome header
        welcome_label = IOSLabel(text='Freevia', font_size=dp(34), bold=True,
                                size_hint_y=None, height=dp(60),
                                halign='center', valign='middle')
        welcome_label.bind(size=welcome_label.setter('text_size'))
        main_layout.add_widget(welcome_label)
        
        # App subtitle
        subtitle_label = IOSLabel(text='İkinci El Eşya Paylaşım Platformu', font_size=dp(16),
                                 color=IOS_COLORS['text_secondary'],
                                 size_hint_y=None, height=dp(30),
                                 halign='center')
        subtitle_label.bind(size=subtitle_label.setter('text_size'))
        main_layout.add_widget(subtitle_label)
        
        # User greeting
        self.greeting_label = IOSLabel(text='Hoş geldiniz!', font_size=dp(18),
                                      color=IOS_COLORS['text_primary'],
                                      size_hint_y=None, height=dp(35),
                                      halign='center')
        self.greeting_label.bind(size=self.greeting_label.setter('text_size'))
        main_layout.add_widget(self.greeting_label)
        
        # Add spacer
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        # Feature cards container
        cards_layout = BoxLayout(orientation='vertical', spacing=dp(15),
                                size_hint_y=None)
        cards_layout.bind(minimum_height=cards_layout.setter('height'))
        
        # Add Item card - Primary feature
        add_item_card = self.create_feature_card(
            '�', 'Eşya Paylaş', 
            'Kullanmadığınız eşyaları fotoğraflayıp paylaşın',
            self.add_item
        )
        cards_layout.add_widget(add_item_card)
        
        # Browse Items card
        browse_card = self.create_feature_card(
            '�️', 'Eşyaları Keşfet', 
            'Çevrenizde paylaşılan eşyaları haritada görün',
            self.browse_items
        )
        cards_layout.add_widget(browse_card)
        
        # My Items card
        my_items_card = self.create_feature_card(
            '📦', 'Paylaştığım Eşyalar', 
            'Daha önce paylaştığınız eşyaları görüntüleyin',
            self.view_my_items
        )
        cards_layout.add_widget(my_items_card)
        
        # Profile card
        profile_card = self.create_feature_card(
            '👤', 'Profil', 
            'Hesap bilgilerinizi görüntüleyin ve düzenleyin',
            self.open_profile
        )
        cards_layout.add_widget(profile_card)
        
        main_layout.add_widget(cards_layout)
        
        # Add spacer before logout
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(30)))
        
        # Logout button
        logout_btn = IOSSecondaryButton(text='Çıkış Yap', 
                                       size_hint_y=None, height=dp(50))
        logout_btn.color = IOS_COLORS['destructive']
        logout_btn.bind(on_press=self.logout)
        main_layout.add_widget(logout_btn)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def create_feature_card(self, icon, title, description, callback):
        """Create an iOS-style feature card"""
        # Card container
        card = BoxLayout(orientation='horizontal', spacing=dp(15),
                        size_hint_y=None, height=dp(80),
                        padding=[dp(20), dp(15)])
        
        # Add card background with shadow
        with card.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.1)
            card.shadow_rect = RoundedRectangle(size=(card.width, card.height-dp(2)), 
                                              pos=(card.x, card.y-dp(2)), 
                                              radius=[dp(16)])
            # Card background
            Color(*IOS_COLORS['card_background'])
            card.bg_rect = RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(16)])
        
        def update_card_graphics(instance, *args):
            instance.shadow_rect.size = (instance.width, instance.height-dp(2))
            instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
        
        card.bind(size=update_card_graphics, pos=update_card_graphics)
        
        # Icon
        icon_label = IOSLabel(text=icon, font_size=dp(28),
                             size_hint_x=None, width=dp(50),
                             halign='center', valign='middle')
        icon_label.bind(size=icon_label.setter('text_size'))
        card.add_widget(icon_label)
        
        # Text content
        text_layout = BoxLayout(orientation='vertical', spacing=dp(2))
        
        title_label = IOSLabel(text=title, font_size=dp(18), bold=True,
                              size_hint_y=None, height=dp(25),
                              halign='left', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))
        
        desc_label = IOSLabel(text=description, font_size=dp(14),
                             color=IOS_COLORS['text_secondary'],
                             size_hint_y=None, height=dp(35),
                             halign='left', valign='top',
                             text_size=(None, None))
        desc_label.bind(size=desc_label.setter('text_size'))
        
        text_layout.add_widget(title_label)
        text_layout.add_widget(desc_label)
        card.add_widget(text_layout)
        
        # Arrow
        arrow_label = IOSLabel(text='›', font_size=dp(24),
                              color=IOS_COLORS['text_secondary'],
                              size_hint_x=None, width=dp(30),
                              halign='center', valign='middle')
        arrow_label.bind(size=arrow_label.setter('text_size'))
        card.add_widget(arrow_label)
        
        # Make card clickable
        class ClickableCard(ButtonBehavior, BoxLayout):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
        
        clickable_card = ClickableCard(orientation='horizontal', spacing=dp(15),
                                     size_hint_y=None, height=dp(80),
                                     padding=[dp(20), dp(15)])
        
        # Copy all children and properties to clickable card
        for child in card.children[:]:
            card.remove_widget(child)
            clickable_card.add_widget(child)
        
        # Add graphics to clickable card
        with clickable_card.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.1)
            clickable_card.shadow_rect = RoundedRectangle(size=(clickable_card.width, clickable_card.height-dp(2)), 
                                                        pos=(clickable_card.x, clickable_card.y-dp(2)), 
                                                        radius=[dp(16)])
            # Card background
            Color(*IOS_COLORS['card_background'])
            clickable_card.bg_rect = RoundedRectangle(size=clickable_card.size, pos=clickable_card.pos, radius=[dp(16)])
        
        clickable_card.bind(size=update_card_graphics, pos=update_card_graphics)
        clickable_card.bind(on_press=callback)
        
        return clickable_card
    
    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def set_user(self, username):
        """Set the current user and update greeting"""
        self.current_user = username
        self.greeting_label.text = f'Hoş geldiniz, {username}!'
    
    def add_item(self, instance):
        """Navigate to add item screen"""
        self.manager.current = 'add_item'
    
    def browse_items(self, instance):
        """Navigate to map screen to browse items"""
        self.manager.current = 'map'
    
    def view_my_items(self, instance):
        """View user's shared items"""
        self.show_ios_popup('Paylaştığım Eşyalar', 'Bu özellik yakında eklenecek!\nBurada daha önce paylaştığınız tüm eşyaları görebileceksiniz.')
    
    def open_profile(self, instance):
        """Navigate to profile screen"""
        self.manager.current = 'profile'
    
    def logout(self, instance):
        """Logout and return to sign in"""
        self.current_user = None
        self.manager.current = 'signin'
    
    def show_ios_popup(self, title, message):
        """Show iOS-style popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        # Message label
        msg_label = IOSLabel(text=message, font_size=dp(16), 
                            color=IOS_COLORS['text_primary'], 
                            text_size=(dp(250), None), halign='center')
        content.add_widget(msg_label)
        
        # OK button
        ok_button = IOSButton(text='Tamam', size_hint_y=None, height=dp(44))
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                     background_color=IOS_COLORS['card_background'],
                     title_color=IOS_COLORS['text_primary'],
                     separator_color=IOS_COLORS['separator'])
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        
        # Set background color
        with self.canvas.before:
            Color(*IOS_COLORS['background'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20), 
                               padding=[dp(20), dp(40), dp(20), dp(20)])
        
        # Header with back button
        header_layout = BoxLayout(orientation='horizontal', 
                                 size_hint_y=None, height=dp(50))
        
        back_btn = IOSSecondaryButton(text='‹ Geri', size_hint_x=None, width=dp(80))
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        title_label = IOSLabel(text='Profil', font_size=dp(28), bold=True,
                              halign='center', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))
        header_layout.add_widget(title_label)
        
        header_layout.add_widget(Widget(size_hint_x=None, width=dp(80)))  # Spacer
        
        main_layout.add_widget(header_layout)
        
        # Profile info card
        profile_card = FloatLayout(size_hint_y=None, height=dp(200))
        
        # Add card background
        with profile_card.canvas.before:
            Color(0, 0, 0, 0.1)
            profile_card.shadow_rect = RoundedRectangle(size=(profile_card.width, profile_card.height-dp(2)), 
                                                       pos=(profile_card.x, profile_card.y-dp(2)), 
                                                       radius=[dp(16)])
            Color(*IOS_COLORS['card_background'])
            profile_card.bg_rect = RoundedRectangle(size=profile_card.size, pos=profile_card.pos, radius=[dp(16)])
        
        def update_profile_card(instance, *args):
            instance.shadow_rect.size = (instance.width, instance.height-dp(2))
            instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
        
        profile_card.bind(size=update_profile_card, pos=update_profile_card)
        
        # Profile content
        profile_content = BoxLayout(orientation='vertical', spacing=dp(15),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                   size_hint=(0.9, 0.8))
        
        # Profile icon
        profile_icon = IOSLabel(text='👤', font_size=dp(60),
                               size_hint_y=None, height=dp(80),
                               halign='center', valign='middle')
        profile_icon.bind(size=profile_icon.setter('text_size'))
        profile_content.add_widget(profile_icon)
        
        # Username
        self.username_label = IOSLabel(text='Kullanıcı', font_size=dp(24), bold=True,
                                      size_hint_y=None, height=dp(40),
                                      halign='center', valign='middle')
        self.username_label.bind(size=self.username_label.setter('text_size'))
        profile_content.add_widget(self.username_label)
        
        # Member since
        self.member_label = IOSLabel(text='Üye olma tarihi: 2025', font_size=dp(16),
                                    color=IOS_COLORS['text_secondary'],
                                    size_hint_y=None, height=dp(30),
                                    halign='center', valign='middle')
        self.member_label.bind(size=self.member_label.setter('text_size'))
        profile_content.add_widget(self.member_label)
        
        profile_card.add_widget(profile_content)
        main_layout.add_widget(profile_card)
        
        # Add spacer
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))
        
        # Action buttons
        edit_btn = IOSButton(text='Profili Düzenle', size_hint_y=None, height=dp(50))
        edit_btn.bind(on_press=self.edit_profile)
        main_layout.add_widget(edit_btn)
        
        change_pwd_btn = IOSSecondaryButton(text='Şifre Değiştir', size_hint_y=None, height=dp(50))
        change_pwd_btn.bind(on_press=self.change_password)
        main_layout.add_widget(change_pwd_btn)
        
        self.add_widget(main_layout)
    
    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def set_user(self, username):
        """Set current user info"""
        self.current_user = username
        self.username_label.text = username
        # You could add more user info here from a database
    
    def go_back(self, instance):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'
    
    def edit_profile(self, instance):
        """Edit profile functionality"""
        self.show_ios_popup('Profil Düzenle', 'Profil düzenleme özelliği yakında eklenecek!')
    
    def change_password(self, instance):
        """Change password functionality"""
        self.show_ios_popup('Şifre Değiştir', 'Şifre değiştirme özelliği yakında eklenecek!')
    
    def show_ios_popup(self, title, message):
        """Show iOS-style popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        msg_label = IOSLabel(text=message, font_size=dp(16), 
                            color=IOS_COLORS['text_primary'], 
                            text_size=(dp(250), None), halign='center')
        content.add_widget(msg_label)
        
        ok_button = IOSButton(text='Tamam', size_hint_y=None, height=dp(44))
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                     background_color=IOS_COLORS['card_background'])
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class AddItemScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user = None
        self.selected_location = None
        self.photo_path = None
        
        # Set background color
        with self.canvas.before:
            Color(*IOS_COLORS['background'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        # Main scroll layout
        scroll = ScrollView()
        main_layout = BoxLayout(orientation='vertical', spacing=dp(20), 
                               padding=[dp(20), dp(40), dp(20), dp(20)],
                               size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Header with back button
        header_layout = BoxLayout(orientation='horizontal', 
                                 size_hint_y=None, height=dp(50))
        
        back_btn = IOSSecondaryButton(text='‹ Ana Sayfa', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=self.go_back)
        header_layout.add_widget(back_btn)
        
        title_label = IOSLabel(text='Eşya Paylaş', font_size=dp(28), bold=True,
                              halign='center', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))
        header_layout.add_widget(title_label)
        
        header_layout.add_widget(Widget(size_hint_x=None, width=dp(120)))  # Spacer
        main_layout.add_widget(header_layout)
        
        # Instructions
        instruction_label = IOSLabel(
            text='Kullanmadığınız eşyaları başkalarıyla paylaşın!\nFotoğraf çekin, açıklama yazın ve konumunu belirleyin.',
            font_size=dp(16), color=IOS_COLORS['text_secondary'],
            size_hint_y=None, height=dp(60),
            halign='center', valign='middle'
        )
        instruction_label.bind(size=instruction_label.setter('text_size'))
        main_layout.add_widget(instruction_label)
        
        # Photo section
        photo_card = FloatLayout(size_hint_y=None, height=dp(200))
        
        with photo_card.canvas.before:
            Color(0, 0, 0, 0.1)
            photo_card.shadow_rect = RoundedRectangle(size=(photo_card.width, photo_card.height-dp(2)), 
                                                     pos=(photo_card.x, photo_card.y-dp(2)), 
                                                     radius=[dp(16)])
            Color(*IOS_COLORS['card_background'])
            photo_card.bg_rect = RoundedRectangle(size=photo_card.size, pos=photo_card.pos, radius=[dp(16)])
        
        def update_photo_card(instance, *args):
            instance.shadow_rect.size = (instance.width, instance.height-dp(2))
            instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
        
        photo_card.bind(size=update_photo_card, pos=update_photo_card)
        
        # Photo content
        photo_content = BoxLayout(orientation='vertical', spacing=dp(15),
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                 size_hint=(0.9, 0.8))
        
        self.photo_label = IOSLabel(text='📷', font_size=dp(60),
                                   size_hint_y=None, height=dp(80),
                                   halign='center', valign='middle')
        self.photo_label.bind(size=self.photo_label.setter('text_size'))
        photo_content.add_widget(self.photo_label)
        
        photo_btn = IOSButton(text='Fotoğraf Çek', size_hint_y=None, height=dp(50))
        photo_btn.bind(on_press=self.take_photo)
        photo_content.add_widget(photo_btn)
        
        photo_card.add_widget(photo_content)
        main_layout.add_widget(photo_card)
        
        # Item details card
        details_card = FloatLayout(size_hint_y=None, height=dp(250))
        
        with details_card.canvas.before:
            Color(0, 0, 0, 0.1)
            details_card.shadow_rect = RoundedRectangle(size=(details_card.width, details_card.height-dp(2)), 
                                                       pos=(details_card.x, details_card.y-dp(2)), 
                                                       radius=[dp(16)])
            Color(*IOS_COLORS['card_background'])
            details_card.bg_rect = RoundedRectangle(size=details_card.size, pos=details_card.pos, radius=[dp(16)])
        
        def update_details_card(instance, *args):
            instance.shadow_rect.size = (instance.width, instance.height-dp(2))
            instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
        
        details_card.bind(size=update_details_card, pos=update_details_card)
        
        # Details content
        details_content = BoxLayout(orientation='vertical', spacing=dp(15),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                   size_hint=(0.9, 0.9))
        
        # Item name
        name_label = IOSLabel(text='Eşya Adı:', font_size=dp(16), bold=True,
                             size_hint_y=None, height=dp(25),
                             halign='left', valign='middle')
        name_label.bind(size=name_label.setter('text_size'))
        details_content.add_widget(name_label)
        
        self.item_name = TextInput(
            hint_text='Örn: Kitap, Sandalye, Telefon...',
            multiline=False,
            size_hint_y=None, height=dp(45),
            font_size=dp(16), padding=[dp(12), dp(12)],
            background_color=[1, 1, 1, 1],
            foreground_color=[0, 0, 0, 1],
            cursor_color=[0, 0.48, 1, 1]
        )
        details_content.add_widget(self.item_name)
        
        # Description
        desc_label = IOSLabel(text='Açıklama:', font_size=dp(16), bold=True,
                             size_hint_y=None, height=dp(25),
                             halign='left', valign='middle')
        desc_label.bind(size=desc_label.setter('text_size'))
        details_content.add_widget(desc_label)
        
        self.item_description = TextInput(
            hint_text='Eşyanın durumu, özellikleri vb...',
            multiline=True,
            size_hint_y=None, height=dp(80),
            font_size=dp(16), padding=[dp(12), dp(12)],
            background_color=[1, 1, 1, 1],
            foreground_color=[0, 0, 0, 1],
            cursor_color=[0, 0.48, 1, 1]
        )
        details_content.add_widget(self.item_description)
        
        details_card.add_widget(details_content)
        main_layout.add_widget(details_card)
        
        # Location section
        location_card = FloatLayout(size_hint_y=None, height=dp(120))
        
        with location_card.canvas.before:
            Color(0, 0, 0, 0.1)
            location_card.shadow_rect = RoundedRectangle(size=(location_card.width, location_card.height-dp(2)), 
                                                        pos=(location_card.x, location_card.y-dp(2)), 
                                                        radius=[dp(16)])
            Color(*IOS_COLORS['card_background'])
            location_card.bg_rect = RoundedRectangle(size=location_card.size, pos=location_card.pos, radius=[dp(16)])
        
        def update_location_card(instance, *args):
            instance.shadow_rect.size = (instance.width, instance.height-dp(2))
            instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
        
        location_card.bind(size=update_location_card, pos=update_location_card)
        
        # Location content
        location_content = BoxLayout(orientation='vertical', spacing=dp(10),
                                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                    size_hint=(0.9, 0.8))
        
        self.location_label = IOSLabel(text='📍 Konum seçilmedi', font_size=dp(16),
                                      color=IOS_COLORS['text_secondary'],
                                      size_hint_y=None, height=dp(30),
                                      halign='center', valign='middle')
        self.location_label.bind(size=self.location_label.setter('text_size'))
        location_content.add_widget(self.location_label)
        
        location_buttons = BoxLayout(orientation='horizontal', spacing=dp(10),
                                   size_hint_y=None, height=dp(45))
        
        current_location_btn = IOSSecondaryButton(text='Mevcut Konum', size_hint_x=0.5)
        current_location_btn.bind(on_press=self.use_current_location)
        location_buttons.add_widget(current_location_btn)
        
        select_location_btn = IOSSecondaryButton(text='Haritadan Seç', size_hint_x=0.5)
        select_location_btn.bind(on_press=self.select_from_map)
        location_buttons.add_widget(select_location_btn)
        
        location_content.add_widget(location_buttons)
        location_card.add_widget(location_content)
        main_layout.add_widget(location_card)
        
        # Share button
        main_layout.add_widget(Widget(size_hint_y=None, height=dp(20)))  # Spacer
        
        share_btn = IOSButton(text='Eşyayı Paylaş', size_hint_y=None, height=dp(55))
        share_btn.bind(on_press=self.share_item)
        main_layout.add_widget(share_btn)
        
        scroll.add_widget(main_layout)
        self.add_widget(scroll)
    
    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def go_back(self, instance):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'
    
    def take_photo(self, instance):
        """Take or select photo"""
        # For now, simulate photo taken
        self.photo_path = "photo_placeholder.jpg"
        self.photo_label.text = '✅ Fotoğraf seçildi'
        self.photo_label.color = IOS_COLORS['success']
        self.show_ios_popup('Fotoğraf', 'Fotoğraf özelliği yakında eklenecek!\nŞimdilik fotoğraf seçildi olarak işaretlendi.')
    
    def use_current_location(self, instance):
        """Use current location"""
        def on_location_found(result):
            if result:
                lat, lon = result
                self.selected_location = (lat, lon)
                self.location_label.text = f'📍 Mevcut konum ({lat:.4f}, {lon:.4f})'
                self.location_label.color = IOS_COLORS['success']
            else:
                self.show_ios_popup('Konum Hatası', 'Mevcut konum alınamadı. Lütfen haritadan seçin.')
        
        get_user_location(callback=on_location_found)
    
    def select_from_map(self, instance):
        """Select location from map"""
        self.show_ios_popup('Harita Seçimi', 'Haritadan konum seçme özelliği yakında eklenecek!')
    
    def share_item(self, instance):
        """Share the item"""
        # Validate inputs
        if not self.item_name.text.strip():
            self.show_ios_popup('Hata', 'Lütfen eşya adını girin.')
            return
        
        if not self.item_description.text.strip():
            self.show_ios_popup('Hata', 'Lütfen eşya açıklamasını girin.')
            return
        
        if not self.photo_path:
            self.show_ios_popup('Hata', 'Lütfen fotoğraf çekin.')
            return
        
        if not self.selected_location:
            self.show_ios_popup('Hata', 'Lütfen konum seçin.')
            return
        
        # For now, just show success message
        self.show_ios_popup('Başarılı!', 'Eşyanız başarıyla paylaşıldı!\nDiğer kullanıcılar artık haritada görebilir.')
        
        # Clear form
        self.item_name.text = ''
        self.item_description.text = ''
        self.photo_path = None
        self.selected_location = None
        self.photo_label.text = '📷'
        self.photo_label.color = IOS_COLORS['text_primary']
        self.location_label.text = '📍 Konum seçilmedi'
        self.location_label.color = IOS_COLORS['text_secondary']
    
    def show_ios_popup(self, title, message):
        """Show iOS-style popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        msg_label = IOSLabel(text=message, font_size=dp(16), 
                            color=IOS_COLORS['text_primary'], 
                            text_size=(dp(250), None), halign='center')
        content.add_widget(msg_label)
        
        ok_button = IOSButton(text='Tamam', size_hint_y=None, height=dp(44))
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                     background_color=IOS_COLORS['card_background'])
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class MapScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set background color
        with self.canvas.before:
            Color(*IOS_COLORS['background'])
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_background, pos=self.update_background)
        
        # Create main layout
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(16), dp(10)])
        
        # Top navigation bar
        nav_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        # Back button
        back_btn = IOSSecondaryButton(text='‹ Ana Sayfa', size_hint_x=None, width=dp(120))
        back_btn.bind(on_press=self.go_back)
        nav_layout.add_widget(back_btn)
        
        # Title label
        title_label = IOSLabel(text='Eşyalar Haritası', font_size=dp(18), bold=True,
                              halign='center', valign='middle')
        title_label.bind(size=title_label.setter('text_size'))
        nav_layout.add_widget(title_label)
        
        # Spacer for balance
        nav_layout.add_widget(Widget(size_hint_x=None, width=dp(120)))
        
        layout.add_widget(nav_layout)
        
        # Search card with iOS styling
        search_card = FloatLayout(size_hint_y=None, height=dp(130))
        
        # Add card background with subtle shadow effect
        with search_card.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.1)
            search_card.shadow_rect = RoundedRectangle(size=(search_card.width, search_card.height-dp(2)), 
                                                     pos=(search_card.x, search_card.y-dp(2)), 
                                                     radius=[dp(16)])
            # Card background
            Color(*IOS_COLORS['card_background'])
            search_card.bg_rect = RoundedRectangle(size=search_card.size, pos=search_card.pos, radius=[dp(16)])
        search_card.bind(size=self.update_search_card, pos=self.update_search_card)
        
        # Search content
        search_content = BoxLayout(orientation='vertical', spacing=dp(10), 
                                 pos_hint={'center_x': 0.5, 'center_y': 0.5},
                                 size_hint=(0.9, 0.8))
        
        # Search input
        self.search_input = TextInput(
            hint_text='Eşya ara (kitap, sandalye, telefon...)...',
            multiline=False,
            size_hint_y=None, 
            height=dp(45),
            font_size=dp(16), 
            padding=[dp(16), dp(12)],
            background_color=[1, 1, 1, 1],
            foreground_color=[0, 0, 0, 1],
            cursor_color=[0, 0.48, 1, 1]
        )
        search_content.add_widget(self.search_input)
        
        # Button layout
        button_layout = BoxLayout(orientation='horizontal', spacing=dp(10), 
                                size_hint_y=None, height=dp(45))
        
        search_button = IOSButton(text='Ara', size_hint_x=0.3)
        search_button.bind(on_press=self.search_items)
        
        my_location_button = IOSSecondaryButton(text='Konumuma Git', size_hint_x=0.7)
        my_location_button.bind(on_press=self.go_to_my_location)
        
        button_layout.add_widget(search_button)
        button_layout.add_widget(my_location_button)
        search_content.add_widget(button_layout)
        
        search_card.add_widget(search_content)
        layout.add_widget(search_card)
        
        # Map view container with iOS styling
        map_container = FloatLayout()
        
        # Add map background card with subtle shadow
        with map_container.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.1)
            map_container.shadow_rect = RoundedRectangle(size=(map_container.width, map_container.height-dp(2)), 
                                                       pos=(map_container.x, map_container.y-dp(2)), 
                                                       radius=[dp(16)])
            # Card background
            Color(*IOS_COLORS['card_background'])
            map_container.bg_rect = RoundedRectangle(size=map_container.size, pos=map_container.pos, radius=[dp(16)])
        map_container.bind(size=self.update_map_card, pos=self.update_map_card)
        
        # Map view with padding
        self.mapview = MapView(zoom=13, lat=41.0082, lon=28.9784,
                              pos_hint={'center_x': 0.5, 'center_y': 0.5},
                              size_hint=(0.98, 0.98))
        map_container.add_widget(self.mapview)
        
        layout.add_widget(map_container)
        self.add_widget(layout)
        
        # Initialize markers
        self._location_marker = None  # User's location marker
        self._item_markers = []  # List of item markers
        
        # Ensure blue pin exists
        ensure_blue_pin_exists()
        
        # Load sample items and user location
        self.load_sample_items()
        self.get_and_show_location()
    
    def update_background(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
    
    def update_search_card(self, instance, *args):
        instance.shadow_rect.size = (instance.width, instance.height-dp(2))
        instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos
    
    def update_map_card(self, instance, *args):
        instance.shadow_rect.size = (instance.width, instance.height-dp(2))
        instance.shadow_rect.pos = (instance.x, instance.y-dp(2))
        instance.bg_rect.size = instance.size
        instance.bg_rect.pos = instance.pos

    def get_and_show_location(self):
        def show_location(result):
            # Schedule UI updates on the main thread
            Clock.schedule_once(lambda dt: self.update_location_ui(result))
            
        get_user_location(callback=show_location)
    
    def load_sample_items(self):
        """Load sample shared items on the map"""
        # Sample items data (in real app, this would come from a database)
        sample_items = [
            {
                'name': 'Eski Kitaplar',
                'description': 'Roman ve hikaye kitapları, temiz durumda',
                'lat': 41.0082 + 0.01,
                'lon': 28.9784 + 0.01,
                'user': 'Ahmet',
                'photo': None
            },
            {
                'name': 'Çalışma Sandalyesi',
                'description': 'Ofis sandalyesi, biraz kullanım izi var',
                'lat': 41.0082 - 0.005,
                'lon': 28.9784 + 0.008,
                'user': 'Ayşe',
                'photo': None
            },
            {
                'name': 'Çocuk Oyuncakları',
                'description': 'Temiz oyuncaklar, çocuk büyüdü',
                'lat': 41.0082 + 0.008,
                'lon': 28.9784 - 0.003,
                'user': 'Mehmet',
                'photo': None
            }
        ]
        
        # Add item markers to map
        for item in sample_items:
            marker = MapMarker(lat=item['lat'], lon=item['lon'])
            marker.item_data = item  # Store item data in marker
            self._item_markers.append(marker)
            self.mapview.add_marker(marker)
    
    def update_location_ui(self, result):
        """Update the UI on the main thread"""
        if result:
            lat, lon = result
            self.mapview.center_on(lat, lon)
            if self._location_marker:
                self.mapview.remove_marker(self._location_marker)
            # Use blue pin for user location
            blue_pin_path = ensure_blue_pin_exists()
            if blue_pin_path:
                self._location_marker = MapMarker(lat=lat, lon=lon, source=blue_pin_path)
                self.mapview.add_marker(self._location_marker)
        else:
            print("Location not available")

    def search_items(self, instance):
        """Search for items on the map"""
        query = self.search_input.text.strip().lower()
        if not query:
            self.show_ios_popup('Arama', 'Lütfen aramak istediğiniz eşya türünü girin.')
            return
        
        # Filter items based on search query
        found_items = []
        for marker in self._item_markers:
            item = marker.item_data
            if (query in item['name'].lower() or 
                query in item['description'].lower()):
                found_items.append(marker)
        
        if found_items:
            # Focus on first found item
            first_item = found_items[0]
            self.mapview.center_on(first_item.lat, first_item.lon)
            self.show_ios_popup('Arama Sonucu', 
                               f'{len(found_items)} eşya bulundu!\nHaritada işaretleri görebilirsiniz.')
        else:
            self.show_ios_popup('Arama Sonucu', 
                               f'"{query}" için eşya bulunamadı.\nFarklı anahtar kelimeler deneyin.')

    def go_to_my_location(self, instance):
        """Go to user's current location"""
        if self._location_marker:
            self.mapview.center_on(self._location_marker.lat, self._location_marker.lon)
        else:
            self.get_and_show_location()
    
    def show_ios_popup(self, title, message):
        """Show iOS-style popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        
        msg_label = IOSLabel(text=message, font_size=dp(16), 
                            color=IOS_COLORS['text_primary'], 
                            text_size=(dp(250), None), halign='center')
        content.add_widget(msg_label)
        
        ok_button = IOSButton(text='Tamam', size_hint_y=None, height=dp(44))
        content.add_widget(ok_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4),
                     background_color=IOS_COLORS['card_background'])
        
        ok_button.bind(on_press=popup.dismiss)
        popup.open()
    
    def go_back(self, instance):
        """Go back to dashboard"""
        self.manager.current = 'dashboard'

    # on_location and on_status are not needed anymore, handled by get_user_location

    def on_status(self, stype, status):
        pass

class FreeviaApp(App):
    def build(self):
        # Set window background color
        from kivy.core.window import Window
        Window.clearcolor = IOS_COLORS['background']
        
        # Ensure blue pin marker exists
        ensure_blue_pin_exists()
        
        # Use smooth slide transition like iOS
        from kivy.uix.screenmanager import SlideTransition
        sm = ScreenManager(transition=SlideTransition(direction='left', duration=0.25))
        sm.add_widget(SignInScreen(name='signin'))
        sm.add_widget(SignUpScreen(name='signup'))
        sm.add_widget(DashboardScreen(name='dashboard'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(AddItemScreen(name='add_item'))
        sm.add_widget(MapScreen(name='map'))
        return sm

if __name__ == '__main__':
    FreeviaApp().run()
