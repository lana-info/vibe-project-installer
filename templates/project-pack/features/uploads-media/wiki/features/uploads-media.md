# Uploads / Media

Use this feature pack if users upload images, files, PDFs, videos, exports, or generated assets.

## Upstream Support

The upstream template includes storage guidance and backend storage service patterns for S3-compatible storage. DigitalOcean Spaces is the documented default for production storage.

## Product Questions

- What file types can users upload?
- Public, private, or shared with selected users?
- Maximum file size?
- Who can upload, view, replace, and delete files?
- Do images need thumbnails, compression, resizing, or moderation?
- How long should files live after the owning record is deleted?

## Setup Checklist

- [ ] Define file types, size limits, and privacy rules in `PRD.md`.
- [ ] Read `docs/STORAGE.md`.
- [ ] Store file ownership and permissions in the backend.
- [ ] Never store durable uploads on a temporary app server filesystem.
- [ ] Add tests for upload authorization and private download access.

