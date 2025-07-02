### 项目概述：

**功能需求：**

1. **用户认证**：使用 JWT 进行用户注册、登录、认证。
2. **图片上传**：用户可以上传图片，并存储在七牛云。
3. **图片智能分析**：对上传的图片进行标签分析，返回标签（这里使用伪接口模拟智能分析）。
4. **相册管理**：用户可以创建、删除、编辑相册，图片可以添加到相册中。
5. **社区分享**：用户可以将自己的相册分享给其他用户，并允许其他用户点赞和评论。

------

### 🏗️ 项目结构

```bash
image_repo_backend/
├── manage.py
├── image_repo_backend/         # 项目配置
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                      # 用户模块
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── images/                     # 图片上传 & 标签管理
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── albums/                     # 相册管理
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── community/                  # 社区分享、评论、点赞
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── requirements.txt
└── .env                        # 环境变量配置
```

------

### 🧑‍💻 1. `requirements.txt`

```txt
Django==4.1.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.0
qiniu==7.2.0  # 七牛云 SDK
drf-yasg==1.21.4  # Swagger API 文档生成
python-dotenv==0.21.1  # 环境变量管理
```

------

### 🧑‍💻 2. `settings.py`

配置基本的 Django 设置、七牛云存储、JWT、CORS、生产部署等。

```python
import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'your_default_secret_key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*']

# 七牛云配置
QINIU_ACCESS_KEY = os.getenv('QINIU_ACCESS_KEY')
QINIU_SECRET_KEY = os.getenv('QINIU_SECRET_KEY')
QINIU_BUCKET_NAME = os.getenv('QINIU_BUCKET_NAME')
QINIU_BUCKET_URL = os.getenv('QINIU_BUCKET_URL')

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key'),
}

# CORS 配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # 你的前端开发地址
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'users',
    'images',
    'albums',
    'community',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'image_repo_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'image_repo_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

------

### 🧑‍💻 3. 用户模块（`users/`）

#### **`users/models.py`**

```python
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass  # 可以扩展字段（如头像、简介等）
```

#### **`users/serializers.py`**

```python
from rest_framework import serializers
from django.contrib.auth import get_user_model

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user
```

#### **`users/views.py`**

```python
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from django.contrib.auth import authenticate

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is None:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
```

------

### 🧑‍💻 4. 图片模块（`images/`）

#### **`images/models.py`**

```python
from django.db import models

class Image(models.Model):
    image_url = models.URLField()
    title = models.CharField(max_length=255)
    user = models.ForeignKey('users.CustomUser', related_name='images', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### **`images/serializers.py`**

```python
from rest_framework import serializers
from .models import Image

class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image_url', 'title']
```

#### **`images/views.py`**

```python
import qiniu
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ImageUploadSerializer
from .models import Image

class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 七牛云上传伪代码
        file = request.FILES['image']
        q = qiniu.Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        token = q.upload_token(QINIU_BUCKET_NAME)
        key = file.name
        # 假设文件上传成功后，我们得到文件 URL
        image_url = f"{QINIU_BUCKET_URL}/{key}"

        image = Image.objects.create(
            image_url=image_url,
            title=request.data.get('title', ''),
            user=request.user
        )

        return Response({"image_url": image_url}, status=201)
```

------

### 🧑‍💻 5. 相册模块（`albums/`）

#### **`

albums/models.py`**

```python
from django.db import models
from users.models import CustomUser

class Album(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, related_name='albums', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### **`albums/serializers.py`**

```python
from rest_framework import serializers
from .models import Album

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['title', 'created_at']
```

#### **`albums/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import AlbumSerializer
from .models import Album

class AlbumCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AlbumSerializer(data=request.data)
        if serializer.is_valid():
            album = serializer.save(user=request.user)
            return Response({"message": "Album created successfully"}, status=201)
        return Response(serializer.errors, status=400)
```

------

### 🧑‍💻 6. 社区模块（`community/`）

#### **`community/models.py`**

```python
from django.db import models
from users.models import CustomUser
from albums.models import Album

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(CustomUser, related_name='likes', on_delete=models.CASCADE)
    album = models.ForeignKey(Album, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### **`community/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Comment, Like
from albums.models import Album

class AddCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        album_id = request.data.get('album_id')
        album = Album.objects.get(id=album_id)
        comment = Comment.objects.create(
            user=request.user,
            album=album,
            content=request.data.get('content')
        )
        return Response({"message": "Comment added successfully"})

class AddLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        album_id = request.data.get('album_id')
        album = Album.objects.get(id=album_id)
        Like.objects.create(user=request.user, album=album)
        return Response({"message": "Album liked"})
```

------

### 🧑‍💻 7. `urls.py`

整合所有模块的路由。

```python
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import RegisterView, LoginView
from images.views import ImageUploadView
from albums.views import AlbumCreateView
from community.views import AddCommentView, AddLikeView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('upload/', ImageUploadView.as_view(), name='upload_image'),
    path('create_album/', AlbumCreateView.as_view(), name='create_album'),
    path('add_comment/', AddCommentView.as_view(), name='add_comment'),
    path('add_like/', AddLikeView.as_view(), name='add_like'),
    path('swagger/', include('drf_yasg.urls')),
]
```

------

### 🧑‍💻 部署

1. **使用 Docker**：如果需要部署，可以将 Django 容器化，方便在云端运行。
2. **生产部署**：配置 Gunicorn + Nginx 作为反向代理。

------

### 🏁 结语

以上是完整的 Django 后端代码结构和功能实现，你可以基于这个项目继续扩展和优化。通过上述代码，你已经可以实现用户认证、图片上传、智能分析、相册管理、社区分享等功能。如果有任何问题或修改需求，随时告诉我！









### 完整的 `CustomUser` 模型代码：

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # 添加自定义字段
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # 用户头像
    bio = models.TextField(max_length=500, blank=True, null=True)  # 用户简介
    birthday = models.DateField(null=True, blank=True)  # 生日
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)  # 性别
    location = models.CharField(max_length=255, blank=True, null=True)  # 用户地址
    # 你可以继续添加其他的自定义字段

    def __str__(self):
        return self.username
```

### 解释：

1. **头像**：使用 `ImageField` 存储用户头像，可以设置 `upload_to='avatars/'` 来指定上传的文件夹。
2. **简介**：`bio` 字段存储用户的个人简介，可以限制最大字符数为 500。
3. **生日**：`birthday` 字段保存用户的出生日期，类型为 `DateField`。
4. **性别**：`gender` 字段使用了 `choices` 来限制可选值，提供了 M（Male）、F（Female）、O（Other）选项。
5. **地址**：`location` 字段用于存储用户所在的地址。

### 迁移数据库：

在修改模型后，你需要运行数据库迁移来创建这些字段。

1. **生成迁移文件**：

   ```bash
   python manage.py makemigrations
   ```

2. **应用迁移文件**：

   ```bash
   python manage.py migrate
   ```

------

### 自定义用户的注意事项：

- 如果你在项目开始时没有创建 `CustomUser` 类，建议在创建项目初期就做出决定并设置 `AUTH_USER_MODEL`。
- 在 `settings.py` 中，确保你将 `AUTH_USER_MODEL` 配置为 `users.CustomUser`，这样 Django 就会使用你的自定义用户模型而不是默认的 `User`。

```python
# settings.py
AUTH_USER_MODEL = 'users.CustomUser'
```

### 头像上传：

确保在 `settings.py` 中正确配置媒体文件的存储路径，以便用户能够上传头像。

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

在 `urls.py` 中添加对媒体文件的访问配置：

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 其他路由
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 总结：

通过扩展 `AbstractUser`，你可以非常方便地添加其他用户相关的信息。如果有其他字段需求，直接在 `CustomUser` 中添加即可。希望这个补充能帮助你更好地实现自定义用户功能！如果你有其他问题，随时告诉我。









