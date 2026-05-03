"""
Login window for TeamAxis.
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from auth.login import AuthManager
from utils.language_manager import get_language_manager
from utils.theme_manager import get_theme_manager

class LoginWindow:
    """Login window interface."""
    
    def __init__(self, on_success_callback):
        """Initialize login window."""
        self.auth_manager = AuthManager()
        self.on_success = on_success_callback
        self.lang = get_language_manager()
        self.theme = get_theme_manager()
        self.window = None
        self.create_window()
    
    def create_window(self):
        """Create login window."""
        self.window = tk.Tk()
        self.window.title(self.lang.t('app_title_login'))
        self.window.geometry("500x550")
        self.window.resizable(False, False)
        self.window.configure(bg=self.theme.get('bg_primary'))
        self.set_window_icon()
        
        # Bring window to front
        self.window.lift()
        self.window.attributes('-topmost', True)
        self.window.after_idle(self.window.attributes, '-topmost', False)
        
        # Center window
        self.center_window()
        
        # Settings frame for language and theme
        settings_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Language selector
        lang_label = tk.Label(settings_frame, text=self.lang.t('menu_language') + ":", font=("Arial", 9), bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary'))
        lang_label.pack(side=tk.LEFT, padx=5)
        
        lang_var = tk.StringVar(value='en' if self.lang.current_language == 'en' else 'zh_TW')
        lang_menu = tk.OptionMenu(settings_frame, lang_var, 'en', 'zh_TW', command=self.change_language)
        lang_menu.config(bg=self.theme.get('bg_secondary'), fg=self.theme.get('fg_primary'), font=("Arial", 9))
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        # Theme selector
        theme_label = tk.Label(settings_frame, text=self.lang.t('menu_theme') + ":", font=("Arial", 9), bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary'))
        theme_label.pack(side=tk.LEFT, padx=(20, 5))
        
        theme_var = tk.StringVar(value=self.theme.current_theme)
        theme_menu = tk.OptionMenu(settings_frame, theme_var, 'light', 'dark', command=self.change_theme)
        theme_menu.config(bg=self.theme.get('bg_secondary'), fg=self.theme.get('fg_primary'), font=("Arial", 9))
        theme_menu.pack(side=tk.LEFT, padx=5)
        
        # Logo and title frame
        logo_title_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        logo_title_frame.pack(pady=20)
        
        # Load and display logo
        self.logo_image = self.load_logo(size=(80, 80))
        if self.logo_image:
            self.logo_label = tk.Label(logo_title_frame, image=self.logo_image, bg=self.theme.get('bg_primary'))
            self.logo_label.image = self.logo_image  # Keep a reference
            self.logo_label.pack(pady=(0, 10))
        
        # Title
        title_label = tk.Label(
            logo_title_frame, 
            text=self.lang.t('app_name'), 
            font=("Arial", 24, "bold"),
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('accent_primary')
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            self.window,
            text=self.lang.t('app_subtitle'),
            font=("Arial", 12),
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('fg_secondary')
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Username frame
        username_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        username_frame.pack(pady=8)
        
        username_label = tk.Label(username_frame, text=self.lang.t('username'), font=("Arial", 10), width=12, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary'))
        username_label.pack(side=tk.LEFT, padx=10)
        
        self.username_entry = tk.Entry(username_frame, width=25, font=("Arial", 10), bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        self.username_entry.pack(side=tk.LEFT, padx=10)
        self.username_entry.focus()
        
        # Password frame
        password_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        password_frame.pack(pady=8)
        
        password_label = tk.Label(password_frame, text=self.lang.t('password'), font=("Arial", 10), width=12, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary'))
        password_label.pack(side=tk.LEFT, padx=10)
        
        self.password_entry = tk.Entry(password_frame, width=25, font=("Arial", 10), show="*", bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        self.password_entry.pack(side=tk.LEFT, padx=10)
        
        # License Key frame
        license_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        license_frame.pack(pady=8)
        
        license_label = tk.Label(license_frame, text=self.lang.t('license_key'), font=("Arial", 10), width=12, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary'))
        license_label.pack(side=tk.LEFT, padx=10)
        
        self.license_entry = tk.Entry(license_frame, width=25, font=("Arial", 10), bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        self.license_entry.pack(side=tk.LEFT, padx=10)
        self.license_entry.insert(0, "XXXX-XXXX-XXXX-XXXX")
        
        # Format license key as user types
        self.license_entry.bind('<KeyRelease>', self.format_license_input)
        
        # Hint for license format
        license_hint = tk.Label(
            self.window,
            text=self.lang.t('license_format_hint'),
            font=("Arial", 8),
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('fg_tertiary')
        )
        license_hint.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        buttons_frame.pack(pady=15)
        
        # Login button
        login_button = tk.Button(
            buttons_frame,
            text=self.lang.t('login'),
            command=self.handle_login,
            bg=self.theme.get('accent_primary'),
            fg="white",
            font=("Arial", 11, "bold"),
            width=10,
            height=1,
            cursor="hand2"
        )
        login_button.pack(side=tk.LEFT, padx=10)
        
        # Register button
        register_button = tk.Button(
            buttons_frame,
            text=self.lang.t('register'),
            command=self.show_register_dialog,
            bg=self.theme.get('accent_secondary'),
            fg="white",
            font=("Arial", 11, "bold"),
            width=10,
            height=1,
            cursor="hand2"
        )
        register_button.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.handle_login())
    
    def change_language(self, language):
        """Change language and refresh window."""
        if self.lang.set_language(language):
            # Recreate window with new language
            self.window.destroy()
            self.create_window()
    
    def change_theme(self, theme):
        """Change theme and refresh window."""
        if self.theme.set_theme(theme):
            # Recreate window with new theme
            self.window.destroy()
            self.create_window()
    
    def load_logo(self, size=(80, 80)):
        """Load logo image from file, theme-aware."""
        # Get script directory and project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up from ui/ to project root
        cwd = os.getcwd()
        
        # Try theme-specific logos first
        is_dark = self.theme.is_dark()
        
        if is_dark:
            # Dark theme - try dark logo variants first
            logo_paths = [
                'logo_dark.png', 'teamaxis_logo_dark.png',
                'assets/logo_dark.png', 'assets/teamaxis_logo_dark.png',
                'logo.png', 'teamaxis_logo.png',
                'assets/logo.png', 'assets/teamaxis_logo.png'
            ]
        else:
            # Light theme - try light logo variants first
            logo_paths = [
                'logo_light.png', 'teamaxis_logo_light.png',
                'assets/logo_light.png', 'assets/teamaxis_logo_light.png',
                'logo.png', 'teamaxis_logo.png',
                'assets/logo.png', 'assets/teamaxis_logo.png'
            ]
        
        for path in logo_paths:
            # Try multiple locations: relative to cwd, relative to project root, and relative to script dir
            possible_paths = [
                path,  # Try relative to current working directory
                os.path.join(cwd, path),  # Try relative to cwd
                os.path.join(project_root, path),  # Try relative to project root
                os.path.join(script_dir, path),  # Try relative to script directory
            ]
            
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    try:
                        img = Image.open(file_path)
                        img = img.resize(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        return photo
                    except Exception as e:
                        print(f"Error loading logo from {file_path}: {e}")
        return None
    
    def set_window_icon(self):
        """Set the window icon using the light-themed logo."""
        # Always use light-themed logo for window icon
        icon_image = self.load_light_logo(size=(32, 32))
        if icon_image:
            try:
                self.window.iconphoto(True, icon_image)
            except Exception as e:
                print(f"Error setting window icon: {e}")
    
    def load_light_logo(self, size=(32, 32)):
        """Load light-themed logo image from file."""
        # Get script directory and project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up from ui/ to project root
        cwd = os.getcwd()
        
        # Always use light logo variants
        logo_paths = [
            'logo_light.png', 'teamaxis_logo_light.png',
            'assets/logo_light.png', 'assets/teamaxis_logo_light.png',
            'logo.png', 'teamaxis_logo.png',
            'assets/logo.png', 'assets/teamaxis_logo.png'
        ]
        
        for path in logo_paths:
            # Try multiple locations: relative to cwd, relative to project root, and relative to script dir
            possible_paths = [
                path,  # Try relative to current working directory
                os.path.join(cwd, path),  # Try relative to cwd
                os.path.join(project_root, path),  # Try relative to project root
                os.path.join(script_dir, path),  # Try relative to script directory
            ]
            
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    try:
                        img = Image.open(file_path)
                        img = img.resize(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        return photo
                    except Exception as e:
                        print(f"Error loading light logo from {file_path}: {e}")
        
        return None
    
    def center_window(self):
        """Center the window on screen."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def format_license_input(self, event=None):
        """Format license key input as user types."""
        # Get current cursor position before any changes
        cursor_pos = self.license_entry.index(tk.INSERT)
        current_text = self.license_entry.get()
        
        # Get the text before cursor (to calculate new position)
        text_before_cursor = current_text[:cursor_pos]
        
        # Remove dashes and spaces, convert to uppercase
        current = current_text.replace('-', '').replace(' ', '').upper()
        if len(current) > 16:
            current = current[:16]
        
        # Format as XXXX-XXXX-XXXX-XXXX
        formatted = ""
        for i, char in enumerate(current):
            if i > 0 and i % 4 == 0:
                formatted += "-"
            formatted += char
        
        # Only update if content changed
        if formatted != current_text:
            # Calculate new cursor position
            # Count alphanumeric characters before cursor in original text
            chars_before = text_before_cursor.replace('-', '').replace(' ', '').upper()
            num_chars_before = len(chars_before)
            
            # Calculate where cursor should be in formatted text
            new_cursor_pos = num_chars_before
            # Add dashes that appear before the cursor position
            for i in range(num_chars_before):
                if i > 0 and i % 4 == 0:
                    new_cursor_pos += 1
            
            # Update the entry
            self.license_entry.delete(0, tk.END)
            self.license_entry.insert(0, formatted)
            
            # Restore cursor position (don't go past end of text)
            new_cursor_pos = min(new_cursor_pos, len(formatted))
            self.license_entry.icursor(new_cursor_pos)
    
    def handle_login(self):
        """Handle login attempt."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        license_key = self.license_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror(self.lang.t('error'), self.lang.t('please_enter_credentials'))
            return
        
        # Check if license is required (admin can skip)
        if license_key == "XXXX-XXXX-XXXX-XXXX" or not license_key:
            license_key = None
        
        success, message = self.auth_manager.login(username, password, license_key)
        
        if success:
            self.window.destroy()
            self.on_success(self.auth_manager)
        else:
            messagebox.showerror("Login Failed", message)
            self.password_entry.delete(0, tk.END)
            if license_key:
                self.license_entry.delete(0, tk.END)
                self.license_entry.insert(0, "XXXX-XXXX-XXXX-XXXX")
    
    def show_register_dialog(self):
        """Show registration dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title(self.lang.t('create_new_account'))
        dialog.geometry("450x500")
        dialog.transient(self.window)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=self.theme.get('bg_primary'))
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f'450x500+{x}+{y}')
        
        # Main container frame
        main_frame = tk.Frame(dialog, bg=self.theme.get('bg_primary'))
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=self.lang.t('create_new_account'),
            font=("Arial", 16, "bold"),
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('accent_primary')
        )
        title_label.pack(pady=10)
        
        # Form fields frame
        form_frame = tk.Frame(main_frame, bg=self.theme.get('bg_primary'))
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Username
        username_frame = tk.Frame(form_frame, bg=self.theme.get('bg_primary'))
        username_frame.pack(fill=tk.X, pady=5)
        tk.Label(username_frame, text=self.lang.t('username'), font=("Arial", 10), width=15, anchor=tk.W, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary')).pack(side=tk.LEFT)
        username_entry = tk.Entry(username_frame, width=25, font=("Arial", 10), bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        username_entry.pack(side=tk.LEFT, padx=5)
        username_entry.focus()
        
        # Password
        password_frame = tk.Frame(form_frame, bg=self.theme.get('bg_primary'))
        password_frame.pack(fill=tk.X, pady=5)
        tk.Label(password_frame, text=self.lang.t('password'), font=("Arial", 10), width=15, anchor=tk.W, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary')).pack(side=tk.LEFT)
        password_entry = tk.Entry(password_frame, width=25, font=("Arial", 10), show="*", bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        password_entry.pack(side=tk.LEFT, padx=5)
        
        # Confirm Password
        confirm_frame = tk.Frame(form_frame, bg=self.theme.get('bg_primary'))
        confirm_frame.pack(fill=tk.X, pady=5)
        tk.Label(confirm_frame, text=self.lang.t('confirm_password'), font=("Arial", 10), width=15, anchor=tk.W, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary')).pack(side=tk.LEFT)
        confirm_password_entry = tk.Entry(confirm_frame, width=25, font=("Arial", 10), show="*", bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        confirm_password_entry.pack(side=tk.LEFT, padx=5)
        
        # Email
        email_frame = tk.Frame(form_frame, bg=self.theme.get('bg_primary'))
        email_frame.pack(fill=tk.X, pady=5)
        tk.Label(email_frame, text=self.lang.t('email'), font=("Arial", 10), width=15, anchor=tk.W, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary')).pack(side=tk.LEFT)
        email_entry = tk.Entry(email_frame, width=25, font=("Arial", 10), bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        email_entry.pack(side=tk.LEFT, padx=5)
        
        # License Key
        license_frame = tk.Frame(form_frame, bg=self.theme.get('bg_primary'))
        license_frame.pack(fill=tk.X, pady=5)
        tk.Label(license_frame, text=self.lang.t('license_key'), font=("Arial", 10), width=15, anchor=tk.W, bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary')).pack(side=tk.LEFT)
        license_entry = tk.Entry(license_frame, width=25, font=("Arial", 10), bg=self.theme.get('entry_bg'), fg=self.theme.get('entry_fg'), insertbackground=self.theme.get('fg_primary'))
        license_entry.pack(side=tk.LEFT, padx=5)
        license_entry.insert(0, "XXXX-XXXX-XXXX-XXXX")
        
        # Format license input
        def format_license(event=None):
            # Get current cursor position before any changes
            cursor_pos = license_entry.index(tk.INSERT)
            current_text = license_entry.get()
            
            # Get the text before cursor (to calculate new position)
            text_before_cursor = current_text[:cursor_pos]
            
            # Remove dashes and spaces, convert to uppercase
            current = current_text.replace('-', '').replace(' ', '').upper()
            if len(current) > 16:
                current = current[:16]
            
            # Format as XXXX-XXXX-XXXX-XXXX
            formatted = ""
            for i, char in enumerate(current):
                if i > 0 and i % 4 == 0:
                    formatted += "-"
                formatted += char
            
            # Only update if content changed
            if formatted != current_text:
                # Calculate new cursor position
                # Count alphanumeric characters before cursor in original text
                chars_before = text_before_cursor.replace('-', '').replace(' ', '').upper()
                num_chars_before = len(chars_before)
                
                # Calculate where cursor should be in formatted text
                new_cursor_pos = num_chars_before
                # Add dashes that appear before the cursor position
                for i in range(num_chars_before):
                    if i > 0 and i % 4 == 0:
                        new_cursor_pos += 1
                
                # Update the entry
                license_entry.delete(0, tk.END)
                license_entry.insert(0, formatted)
                
                # Restore cursor position (don't go past end of text)
                new_cursor_pos = min(new_cursor_pos, len(formatted))
                license_entry.icursor(new_cursor_pos)
        
        license_entry.bind('<KeyRelease>', format_license)
        
        # Hint
        hint_label = tk.Label(
            form_frame,
            text=self.lang.t('license_required'),
            font=("Arial", 8),
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('fg_tertiary')
        )
        hint_label.pack(pady=5)
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm_password = confirm_password_entry.get()
            email = email_entry.get().strip()
            license_key = license_entry.get().strip()
            
            # Validation
            if not username:
                messagebox.showerror(self.lang.t('error'), self.lang.t('username_required'))
                return
            
            if not password:
                messagebox.showerror(self.lang.t('error'), self.lang.t('password_required'))
                return
            
            if password != confirm_password:
                messagebox.showerror(self.lang.t('error'), self.lang.t('passwords_not_match'))
                return
            
            if len(password) < 6:
                messagebox.showerror(self.lang.t('error'), self.lang.t('password_min_length'))
                return
            
            if not license_key or license_key == "XXXX-XXXX-XXXX-XXXX":
                messagebox.showerror(self.lang.t('error'), self.lang.t('license_key_required_registration'))
                return
            
            # Register user
            success, message = self.auth_manager.register(username, password, email, license_key)
            
            if success:
                messagebox.showinfo(self.lang.t('success'), message + "\n" + self.lang.t('login_successful'))
                dialog.destroy()
            else:
                messagebox.showerror(self.lang.t('registration_failed'), message)
        
        # Buttons frame at bottom
        buttons_frame = tk.Frame(main_frame, bg=self.theme.get('bg_primary'))
        buttons_frame.pack(pady=15)
        
        # Register button (Confirm)
        register_button = tk.Button(
            buttons_frame,
            text=self.lang.t('register'),
            command=register,
            bg=self.theme.get('accent_secondary'),
            fg="white",
            font=("Arial", 11, "bold"),
            width=15,
            height=1,
            cursor="hand2"
        )
        register_button.pack(side=tk.LEFT, padx=8)
        
        # Cancel button
        cancel_button = tk.Button(
            buttons_frame,
            text=self.lang.t('cancel'),
            command=dialog.destroy,
            bg=self.theme.get('bg_tertiary'),
            fg="white",
            font=("Arial", 11),
            width=15,
            height=1,
            cursor="hand2"
        )
        cancel_button.pack(side=tk.LEFT, padx=8)
        
        # Bind Enter key to register
        dialog.bind('<Return>', lambda e: register())
    
    def run(self):
        """Run the login window."""
        self.window.mainloop()

