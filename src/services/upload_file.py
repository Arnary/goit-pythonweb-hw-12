import cloudinary
import cloudinary.uploader

class UploadFileService:
    """
    Service for uploading files to Cloudinary.

    Attributes:
    - cloud_name: Cloudinary cloud name.
    - api_key: Cloudinary API key.
    - api_secret: Cloudinary API secret.

    Methods:
    - upload_file(file, username) -> str: Upload a file to Cloudinary and return the source URL.

    Static Methods:
    - None
    """
    def __init__(self, cloud_name, api_key, api_secret):
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
