from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

# Create your models here.
HTTP   = 1
HTTPS  = 2
SOCKS4 = 4
SOCKS5 = 8
PROXYTYPE = (
  (1, 'HTTP'  ),
  (2, 'HTTPS' ),
  (4, 'SOCKS4'),
  (8, 'SOCKS5'),
)

def validate_python_script(script):
    try:
        exec(script)
    except SyntaxError as e:
        raise ValidationError('Not a valid python script: %s' % str(e))

class Source(models.Model):
    name = models.CharField(max_length=64, unique=True)
    script = models.CharField(max_length=2048, validators=[validate_python_script])

    last_fetch_time = models.DateTimeField(auto_now=True, blank=True)
    last_fetch_success = models.BooleanField(default=False)
    last_fetch_resources_found = models.IntegerField(default=0)


class Endpoint(models.Model):
    ip = models.CharField(max_length=32)
    port = models.IntegerField(default=0)
    proxy_types = models.IntegerField(default=HTTP, choices=PROXYTYPE)
    sources = models.ManyToManyField(Source)

    last_checked_time = models.DateTimeField(auto_now=True, blank=True)
    last_checked_success = models.BooleanField(default=False)
    last_checked_delay_ms = models.IntegerField(default=0)

    class Meta:
        unique_together = (('ip', 'port'),)

    @property
    def proxy_types_str(self):
        s = ''
        for e in PROXYTYPE:
            if self.proxy_types & e[0]:
                s = s + '|' + e[1] if s else e[1]
        return s

    @property
    def source_names(self):
        n = ''
        for s in self.sources.all():
            n = n + ',' + s.name if n else s.name
        return n
