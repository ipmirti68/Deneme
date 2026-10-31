import asyncio
from playwright.async_api import async_playwright

CIKIS = "ulusal.m3u"

KANALLAR = [
    {"isim": "STAR ", "url": "https://www.startv.com.tr/canli-yayin", "logo": ""},
    {"isim": "SHOW ", "url": "https://www.showtv.com.tr/canli-yayin", "logo": ""},
    {"isim": "TRT ", "url": "https://www.tabii.com/tr/watch/live/trt1?trackId=150002", "logo": ""},

]


async def al(browser, kanal):
    print(f"[*] {kanal['isim']}")
    ctx = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    page = await ctx.new_page()
    bulunan = []

    async def resp(r):
        u = r.url
        if ".m3u8" in u and ".ts" not in u:
            if u not in bulunan:
                bulunan.append(u)
                print(f"   m3u8: {u[:150]}")

    page.on("response", resp)
    try:
        await page.goto(kanal["url"], wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(7000)
        try:
            await page.mouse.click(300, 300)
        except:
            pass
        await page.wait_for_timeout(15000)
    except Exception as e:
        print(f" hata {e}")

    await ctx.close()
    if bulunan:
        # master/index olanlari onceliklendir
        for x in bulunan:
            if "master" in x:
                return x
        return bulunan[-1]
    return None

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(headless=True, args=["--no-sandbox", "--autoplay-policy=no-user-gesture-required"])
        m3u = "#EXTM3U\n"
        for k in KANALLAR:
            link = await al(br, k)
            if link:
                print(f"[+] {k['isim']} OK")
                m3u += f'#EXTINF:-1 tvg-name="{k["isim"]}",{k["isim"]}\n{link}\n'
            else:
                print(f"[-] {k['isim']} bulunamadi")
        await br.close()
        open(CIKIS, "w", encoding="utf-8").write(m3u)
        print("DOSYA YAZILDI")

asyncio.run(main())
