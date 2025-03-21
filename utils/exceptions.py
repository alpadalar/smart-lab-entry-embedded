"""
Laboratuvar giriş sisteminde kullanılan özel hata sınıfları.
"""


class LaboratuvarGirisHatasi(Exception):
    """Laboratuvar giriş sistemi için temel hata sınıfı."""
    pass


class InitializationError(LaboratuvarGirisHatasi):
    """Donanım veya yazılım başlatma hatası."""
    pass


class HardwareError(LaboratuvarGirisHatasi):
    """Donanım hatası."""
    pass


class NFCInitializationError(InitializationError):
    """NFC okuyucu başlatma hatası."""
    pass


class LEDInitializationError(InitializationError):
    """LED başlatma hatası."""
    pass


class BuzzerInitializationError(InitializationError):
    """Buzzer başlatma hatası."""
    pass


class RelayInitializationError(InitializationError):
    """Röle başlatma hatası."""
    pass


class LCDInitializationError(InitializationError):
    """LCD başlatma hatası."""
    pass


class I2CError(HardwareError):
    """I2C iletişim hatası."""
    pass


class GPIOError(HardwareError):
    """GPIO pin hatası."""
    pass


class AuthenticationError(LaboratuvarGirisHatasi):
    """Kimlik doğrulama hatası."""
    pass


class CardReadError(HardwareError):
    """Kart okuma hatası."""
    pass


class ConfigError(LaboratuvarGirisHatasi):
    """Yapılandırma dosyası hatası."""
    pass


class ApiError(LaboratuvarGirisHatasi):
    """API iletişim hatası."""
    pass


class ApiConnectionError(ApiError):
    """API bağlantı hatası."""
    pass


class ApiResponseError(ApiError):
    """API yanıt hatası."""
    pass


class ApiAuthenticationError(ApiError):
    """API kimlik doğrulama hatası."""
    pass 