from fastmcp.server.auth.providers.bearer import RSAKeyPair

# RSA 키 쌍 생성
key_pair = RSAKeyPair.generate()

# 공개키 파일로 저장
with open("public.pem", "w") as f:
    f.write(key_pair.public_key)

token = key_pair.create_token(
    subject="dev-user",
    issuer="https://aidesk.koreatimes.co.kr",
    audience="calculator",
    scopes=["read", "write"],
    expires_in_seconds=24 * 60 * 60   # 하루(86400초)
)

# JWT 토큰 출력
print(f"Test token: {token}")
