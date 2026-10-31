import asyncio
from playwright.async_api import async_playwright

CIKIS_DOSYASI = "ulusal.m3u"

KANALLAR = [
    {
        "isim": "【entity-Star¦canonical_name=Star TV】 TV",
        "url": "https://www.startv.com.tr/canli-yayin",
        "anahtar": "720p.m3u8",
        "logo": "https://img-startv.mncdn.com/assets/images/logo.png"
    },
    {
        "isim": "【entity-Show¦canonical_name=Show TV】 TV",
        "url": "https://www.showtv.com.tr/canli-yayin",
        "anahtar": "master.m3u8", 
        "logo": "https://mo.ciner.com.tr/showtv/iletisim/logo.png"
    },
    {
        "isim": "【entity-Show¦canonical_name=Show TV】 TV",
        "url": "https://www.showtv.com.tr/canli-yayin",
        "anahtar": "master.m3u8", 
        "logo": "https://mo.ciner.com.tr/showtv/iletisim/logo.png"
    }
]

async def get_m3u8_link(browser, kanal):
    print(f"[*] {kanal['isim']} aranıyor...")
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
    page = await context.new_page()
    m3u8_list = []

    async def handle_response(response):
        url = response.url
        if kanal["anahtar"] in url and ".m3u8" in url and ".ts" not in url:
            if "dai" not in url and "ad" not in url.lower():
                if url not in m3u8_list:
                    m3u8_list.append(url)
                    print(f"  -> Aday: {url[:100]}...")

    page.on("response", handle_response)
    
    try:
        await page.goto(kanal["url"], wait_until="domcontentloaded", timeout=40000)
        await page.wait_for_timeout(6000)
        
        # Ses için en kritik yer: play'e tıklamak
        try:
            await page.mouse.click(400, 400)
            await page.locator("video").first.click(timeout=3000)
        except:
            pass
        
        await page.wait_for_timeout(12000) # ses streami için bekle

    except Exception as e:
        print(f"[!] {kanal['isim']} hata: {e}")

    await context.close()
    
    if m3u8_list:
        m3u8_list.sort(key=len, reverse=True)
        return m3u8_list[0]
    return None

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--autoplay-policy=no-user-gesture-required"]
        )
        
        m3u_icerik = "#EXTM3U\n"
        
        for kanal in KANALLAR:
            link = await get_m3u8_link(browser, kanal)
            if link:
                print(f"[+] {kanal['isim']} OK -> {link[:60]}")
                m3u_icerik += f'#EXTINF:-1 tvg-id="{kanal["isim"]}" tvg-name="{kanal["isim"]}" tvg-logo="{kanal["logo"]}",{kanal["isim"]}\n'
                m3u_icerik += f'{link}\n'
            else:
                print(f"[-] {kanal['isim']} bulunamadı")
        
        await browser.close()
        
        with open(CIKIS_DOSYASI, "w", encoding="utf-8") as f:
            f.write(m3u_icerik)
        print(f"\n[+] Bitti -> {CIKIS_DOSYASI}")

if __name__ == "__main__":
    asyncio.run(main())
