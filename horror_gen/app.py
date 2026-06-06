import os
import random
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# =============================================
# 🤖 OpenAI API konfiguratsiyasi
# =============================================
# API kalitni environment variable orqali yoki to'g'ridan-to'g'ri yozing
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# OpenAI API mavjudligini tekshirish
def is_openai_available():
    return bool(OPENAI_API_KEY)

def generate_ai_story(location, character, horror_type):
    """OpenAI API orqali dahshatli hikoya generatsiya qilish."""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""Sen professional dahshatli hikoya yozuvchisissan. Quyidagi parametrlarga asosan o'zbek tilida qisqa, dahshatli va sehrli hikoya yoz (300-400 so'z):

Joylashuv: {location}
Bosh qahramon: {character}
Dahshat turi: {horror_type}

Hikoya talablari:
- O'zbek tilida yozilsin
- Dahshatli, sirli va hayajonli bo'lsin
- Qisqa lekin ta'sirli
- Oxiri kutilmagan twist bilan tugasin
- Atmosfera yaratuvchi detallar ko'p bo'lsin
- {horror_type} janriga mos bo'lsin

Faqat hikoyani yoz, boshqa izoh qo'shma."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen tajribali dahshatli hikoya yozuvchisissan. O'zbek tilida qisqa, ta'sirli dahshatli hikoyalar yozasan."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.9,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        return None
    except Exception as e:
        print(f"OpenAI API xatosi: {e}")
        return None


def generate_ai_image_prompt(location, character, horror_type):
    """OpenAI API orqali kreativ rasm prompti generatsiya qilish."""
    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""Create a highly detailed, cinematic image generation prompt (for Midjourney or DALL-E) based on these parameters:

Location: {location}
Character: {character}
Horror type: {horror_type}

Requirements:
- Write ONLY in English
- Make it extremely vivid and atmospheric
- Include camera angle, lighting, mood, art style details
- Add --ar 16:9 --style raw at the end
- Maximum 100 words
- Make it perfect for YouTube thumbnail or TikTok cover

Output ONLY the prompt text, nothing else."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert prompt engineer for AI image generation. You create vivid, cinematic horror scene prompts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        return None
    except Exception as e:
        print(f"OpenAI API xatosi: {e}")
        return None


# =============================================
# 📚 Kontent bazasi — hikoyalar, joylashuvlar, personajlar
# =============================================

LOCATIONS = [
    "Tashlab ketilgan shifoxona",
    "Tashlab ketilgan maktab",
    "Zulmatli o'rmon",
    "Eski metro bekati",
    "Sirli laboratoriya",
    "Vayronaga aylangan cherkov",
    "Qorong'u tunel",
    "Tashlandiq fabrika",
    "Eski qabriston",
    "Suv osti bunkeri",
]

CHARACTERS = [
    "Tungi qorovul",
    "Adashib qolgan blogger",
    "Dasturchi",
    "Guruh talabalari",
    "Yolg'iz sayohatchi",
    "Shifokor",
    "Jurnalist",
    "Arxeolog",
    "O'qituvchi",
    "Haydovchi",
]

HORROR_TYPES = [
    "Kabus (Monstr)",
    "Psixologik triller",
    "Qoidalar dahshati (Rules Horror)",
    "Paranormal hodisalar",
    "Kosmik dahshat (Cosmic Horror)",
    "Epidemiya (Survival Horror)",
]

# =============================================
# 📖 Hikoyalar shablonlari (fallback / offline rejim)
# =============================================

STORY_TEMPLATES = {
    "Kabus (Monstr)": [
        "{char} {loc} ichiga kirganida, devorlardagi tirnash izlarini ko'rdi. Izlar tobora kattaroq bo'lib borardi — go'yoki mavjudot ham o'sib borardi. Birdan devorning narigi tomonidan nafas tovushi eshitildi. U yo'lakdan yugurib chiqmoqchi bo'ldi, lekin barcha eshiklar o'z-o'zidan yopilib qoldi. Oynadan ko'ringan aks esa uning emasdi...",
        "Soat 2:47. {char} {loc} da yolg'iz qoldi. Radio o'z-o'zidan yondi va baland ovozda layli aytila boshladi. Derazadan tashqariga qaradi — hovlida bola turardi. Lekin bolaning yuzi yo'q edi. Bola sekin qo'lini ko'tardi va barmoq bilan {char}ni ko'rsatdi. Keyin qorong'ulikda erib ketdi...",
        "{char} {loc} ning pastki qavatiga tushdi. U yerda devorga yozilgan edi: 'SEN HAM QOLASAN'. Orqasidan oyoq tovushi eshitildi — lekin u yolg'iz kirganini aniq bilardi. Chiroq o'chdi. Qayta yonganda, devorga yana bitta gap qo'shilgandi: 'ENDI KECH'.",
    ],
    "Psixologik triller": [
        "{char} har kuni {loc} yonidan o'tardi. Bir kuni derazada o'zining aksini ko'rdi — lekin u boshqa kiyimda edi. Ertasi kuni yana ko'rdi — bu safar uning aksi qo'l silkidi. Uchinchi kuni aks derazadan chiqib keldi...",
        "{char} {loc} da uyg'ondi. Telefonida 47 ta javobsiz qo'ng'iroq bor edi — hammasi o'zining raqamidan. So'nggi xabar: 'Uyg'onma. Bu tush. Agar uyg'onsang, MEN yo'qolaman'. {char} atrofga qaradi — xona tanish edi. Juda tanish. Bu uning bolalik xonasi edi. Lekin u bu xonadan 20 yil oldin ko'chib ketgan...",
        "Kundalik yozuvi, 7-kun. {char} {loc} da 7 kun oldin adashdi. Eng g'alati narsa — u har kuni bir xil eshikdan chiqadi va har kuni bir xil yo'lakka qaytadi. Bugun yana chiqdi. Lekin bu safar yo'lakda o'zining jasadi yotardi. Jasadning qo'lida kundalik bor edi — va unda 300 kun yozilgan...",
    ],
    "Qoidalar dahshati (Rules Horror)": [
        "QOIDALAR — {loc}:\n1. Soat 3:00 dan keyin yo'lakka chiqmang.\n2. Agar {char} 'Salom' degan ovoz eshitsa, javob bermang.\n3. Ko'zguga ASLO qaramang.\n4. Agar siz bu qoidalarni o'qiyotgan bo'lsangiz, demak siz allaqachon {loc} ichida qolgan ekansiz.\n5. Oxirgi qoida: BU QOIDALAR SIZNI HIMOYA QILMAYDI. Ular SIZNI KUZATAYOTGAN NARSAGA qachon sizni topish kerakligini aytadi.",
        "{char} {loc} eshigida yozuvni o'qidi:\n📜 QOIDALAR:\n- Hech kimga ishmang.\n- 3-qavatga CHIQMANG.\n- Agar lift o'z-o'zidan ochilsa — KIRMANG.\n- Bu yozuvni o'qigan bo'lsangiz — orqangizga qaramang.\n{char} orqasiga qaradi. Orqasida hech kim yo'q edi. Lekin devorga yangi yozuv paydo bo'ldi: 'AYTDIM-KU. ENDI U SENI KO'RDI.'",
        "{char} {loc} ga kirdi va stolda qog'oz topdi:\n'Xush kelibsiz. Bir nechta qoida bor:\n1. Chiroqni o'chirmang.\n2. Agar ovoz eshitsangiz — bu men emasman.\n3. Agar men eshikdan kirsam — bu men emasman.\n4. Agar hamma narsa tinch bo'lsa — ENG XAVFLI PAYT SHU.'\nShundan keyin chiroq miltilladi. Va eshik sekin ochildi...",
    ],
    "Paranormal hodisalar": [
        "{char} {loc} da ishlash uchun keldi. Birinchi kechasi shifti shipillab ovoz chiqardi. Ikkinchi kechasi stul o'z-o'zidan surildi. Uchinchi kechasi — {char} stolda o'tirganida, yonidagi bo'sh stulda kimdir nafas olayotganini his qildi. To'rtinchi kechasi — u kelmadi. Besh kechasi — uning o'rniga boshqa odam keldi. Lekin xodimlar aytishicha, yangi odam... {char}ning o'ziga o'xshardi.",
        "{char} {loc} ning eski arxivini tekshirardi. Papkalarning birida 1987-yilgi suratlar bor edi. Eng oxirgi suratda — {loc} ning eski ko'rinishi. Lekin suratning chetida bir odam turardi. {char} kattalashtirdi va muzlab qoldi — suratdagi odam... o'zi edi. Va suratning orqasiga yozilgan edi: 'SEN QAYTDING.'",
        "{char} {loc} dagi eski radioni yoqdi. Radio 30 yil oldin o'chirilgan edi. Lekin efirda ovoz bor edi — kimdir {char}ning ismini takrorlar, tinmay, soatlab. {char} radioni o'chirdi. Ovoz to'xtamadi. Chunki ovoz radiodan emas — devor ichidan kelayotgan edi.",
    ],
    "Kosmik dahshat (Cosmic Horror)": [
        "{char} {loc} da g'alati signalni ushladi. Signal kosmosdan kelayotgan edi — lekin uni JO'NATGAN manzil... Yerning o'zi edi. Signal mazmuni: 'BARCHASI TUGADI. SIZLAR FAQAT XO'TIRA.' {char} osmonga qaradi. Osmon bor edi. Lekin yulduzlar yo'q edi. Yulduzlar HECH QACHON bo'lmaganday...",
        "{char} {loc} ning pastki qavatida g'alati tosh topdi. Tosh iliq edi — go'yoki tirik. Toshni qo'liga olganida, koinotning haqiqiy o'lchamini ko'rdi. Inson — bu faqat hujayra. Yer — bu faqat zarracha. Borlikning o'zi — bu tushunib bo'lmas mavjudotning tushi. Va u endi uyg'onmoqda...",
        "{char} {loc} dagi teleskopni osmonga qaratdi. Lekin ko'rgan narsa yulduzlar emas edi. Qorong'ulikda ulkan KO'Z bor edi — va u to'g'ridan-to'g'ri {char}ga qarayotgan edi. {char} teleskopni tushirdi. Ko'z hali ham ko'rinyapdi edi — lekin endi teleskopsiz, oddiy ko'z bilan. Chunki u yaqinlashib kelayotgan edi.",
    ],
    "Epidemiya (Survival Horror)": [
        "51-kun. {char} {loc} da yashirinib yotibdi. Tashqarida ular yurishadi — bir zamonlar odam bo'lganlar. Radio sukut saqlaydi. Oziq-ovqat 3 kunga yetadi. Bugun eshikni tiqillatishdi — 3 marta. Bu 'xavfsiz' signali edi. Lekin bu signalni faqat {char} bilardi. U YOLG'IZ edi. Demak, tiqillatgan narsa... signalni TINGLAGAN.",
        "{char} {loc} dan chiqib, tashqarini ko'rdi. Shahar bo'sh. Mashinalar to'xtagan. Odamlar yo'q. Faqat devor yozuvlari bor: 'NAFAS OLMANG'. {char} chuqur nafas oldi — va havoning mazasini sezdi. Shirin. Juda shirin. Shunda tushundi — nima uchun odamlar yo'q. Va nima uchun u dafatan juda och bo'lib qoldi...",
        "{char} {loc} dagi radio stansiyasini topdi. Efirda avtomatik xabar takrorlanardi: 'Diqqat! Infeksiya 98% ga yetdi. Inson turi amalda tugadi. Agar siz buni eshitayotgan bo'lsangiz — yuguring. Agar yugura olmayotgan bo'lsangiz... ehtimol siz ALLAQACHON o'zgargansiz.' {char} qo'liga qaradi. Barmoqlari g'alati rangga kirib borardi...",
    ],
}

# =============================================
# 📸 Image prompt shablonlari (fallback)
# =============================================

IMAGE_PROMPT_TEMPLATES = [
    "Cinematic horror scene: {char_en} standing alone inside a dark, abandoned {loc_en}. Thick fog rolling across the floor, flickering red neon lights casting eerie shadows, {horror_detail}. Photorealistic, Unreal Engine 5, 8K, ultra detailed, volumetric lighting --ar 16:9 --style raw",
    "Dark atmospheric horror illustration: {char_en} exploring a decaying {loc_en} at midnight. Moonlight streaming through broken windows, {horror_detail}, dust particles floating in the air. Hyper-realistic digital art, cinematic composition, dramatic chiaroscuro lighting --ar 16:9 --style raw",
    "Terrifying cinematic still: POV shot of {char_en} in a nightmare {loc_en}. {horror_detail}, wet reflective floors, emergency lights flickering. Film grain, anamorphic lens flare, horror movie aesthetic, 35mm film look --ar 16:9 --style raw",
]

HORROR_DETAILS = {
    "Kabus (Monstr)": "a massive shadowy creature lurking in the corner with glowing red eyes, long twisted claws scraping the walls",
    "Psixologik triller": "distorted reflections in cracked mirrors showing a different version of the character, unsettling symmetry",
    "Qoidalar dahshati (Rules Horror)": "mysterious glowing text written on the walls in blood-red light, forbidden symbols and warnings everywhere",
    "Paranormal hodisalar": "ghostly translucent figures floating in the background, objects levitating mid-air, spectral green mist",
    "Kosmik dahshat (Cosmic Horror)": "an impossibly large cosmic eye visible through the ceiling, tentacles of darkness reaching from every corner, alien geometry",
    "Epidemiya (Survival Horror)": "abandoned medical equipment, biohazard signs, quarantine tape, a lone gas mask on the floor, toxic green atmosphere",
}

LOC_EN = {
    "Tashlab ketilgan shifoxona": "hospital",
    "Tashlab ketilgan maktab": "school",
    "Zulmatli o'rmon": "dark forest",
    "Eski metro bekati": "subway station",
    "Sirli laboratoriya": "laboratory",
    "Vayronaga aylangan cherkov": "ruined church",
    "Qorong'u tunel": "dark tunnel",
    "Tashlandiq fabrika": "abandoned factory",
    "Eski qabriston": "old graveyard",
    "Suv osti bunkeri": "underground bunker",
}

CHAR_EN = {
    "Tungi qorovul": "a night security guard",
    "Adashib qolgan blogger": "a lost blogger",
    "Dasturchi": "a programmer",
    "Guruh talabalari": "a group of students",
    "Yolg'iz sayohatchi": "a lone traveler",
    "Shifokor": "a doctor",
    "Jurnalist": "a journalist",
    "Arxeolog": "an archaeologist",
    "O'qituvchi": "a teacher",
    "Haydovchi": "a driver",
}


def generate_story(location, character, horror_type):
    """Tanlangan parametrlarga asosan shablon hikoya generatsiya qilish."""
    templates = STORY_TEMPLATES.get(horror_type, STORY_TEMPLATES["Kabus (Monstr)"])
    template = random.choice(templates)
    return template.format(char=character, loc=location)


def generate_image_prompt(location, character, horror_type):
    """Shablon asosida rasm promti generatsiya qilish."""
    loc_en = LOC_EN.get(location, "abandoned building")
    char_en = CHAR_EN.get(character, "a lone figure")
    horror_detail = HORROR_DETAILS.get(horror_type, "eerie shadows and mysterious fog")
    template = random.choice(IMAGE_PROMPT_TEMPLATES)
    return template.format(char_en=char_en, loc_en=loc_en, horror_detail=horror_detail)


# =============================================
# 🌐 Flask Routes
# =============================================

@app.route("/", methods=["GET", "POST"])
def index():
    story = None
    image_prompt = None
    ai_used = False
    selected = {"location": "", "character": "", "horror_type": ""}

    if request.method == "POST":
        loc = request.form.get("location", "")
        char = request.form.get("character", "")
        h_type = request.form.get("horror_type", "")
        use_ai = request.form.get("use_ai", "off")

        selected = {"location": loc, "character": char, "horror_type": h_type}

        if use_ai == "on" and is_openai_available():
            # AI bilan generatsiya
            ai_story = generate_ai_story(loc, char, h_type)
            ai_prompt = generate_ai_image_prompt(loc, char, h_type)
            if ai_story:
                story = ai_story
                ai_used = True
            else:
                story = generate_story(loc, char, h_type)

            if ai_prompt:
                image_prompt = ai_prompt
            else:
                image_prompt = generate_image_prompt(loc, char, h_type)
        else:
            story = generate_story(loc, char, h_type)
            image_prompt = generate_image_prompt(loc, char, h_type)

    return render_template(
        "index.html",
        locations=LOCATIONS,
        characters=CHARACTERS,
        horror_types=HORROR_TYPES,
        story=story,
        image_prompt=image_prompt,
        selected=selected,
        ai_available=is_openai_available(),
        ai_used=ai_used,
    )


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """AJAX endpoint — AI yoki shablon orqali hikoya generatsiya qilish."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON ma'lumot kerak"}), 400

    loc = data.get("location", "")
    char = data.get("character", "")
    h_type = data.get("horror_type", "")
    use_ai = data.get("use_ai", False)

    ai_used = False

    if use_ai and is_openai_available():
        story = generate_ai_story(loc, char, h_type)
        prompt = generate_ai_image_prompt(loc, char, h_type)
        if story:
            ai_used = True
        else:
            story = generate_story(loc, char, h_type)

        if not prompt:
            prompt = generate_image_prompt(loc, char, h_type)
    else:
        story = generate_story(loc, char, h_type)
        prompt = generate_image_prompt(loc, char, h_type)

    return jsonify({
        "story": story,
        "image_prompt": prompt,
        "ai_used": ai_used,
        "location": loc,
        "character": char,
        "horror_type": h_type,
    })


@app.route("/api/status", methods=["GET"])
def api_status():
    """API holatini tekshirish."""
    return jsonify({
        "ai_available": is_openai_available(),
        "total_locations": len(LOCATIONS),
        "total_characters": len(CHARACTERS),
        "total_horror_types": len(HORROR_TYPES),
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
