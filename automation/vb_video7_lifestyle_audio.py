from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

ROOT = Path('vb_video7_lifestyle_audio')
CUE_DIR = ROOT / 'voice_cues'
TMP = Path('tmp_vb_video7_lifestyle')
ROOT.mkdir(exist_ok=True)
CUE_DIR.mkdir(exist_ok=True)
TMP.mkdir(exist_ok=True)

TOTAL_MS = 690_000
TARGET_DBFS = -18.0
VOICE = 'hi-IN-SwaraNeural'

CUES = [
    (2.0, 'विश्रांति बिन्दु। पाठ सात। योगासन, प्रकृति, परिश्रम, मनोदशा और आचरण का अनुभव-आधारित निरीक्षण।'),
    (12.0, 'यह सामग्री केवल दीक्षित साधकों, अधिकृत शिक्षकों और आंतरिक कार्यक्रम उपयोग के लिए है।'),
    (22.0, 'आज हम कोई नई साधना नहीं जोड़ेंगे। हम देखेंगे कि शरीर, मनोदशा और आचरण की अलग-अलग स्थितियों का हमारे पहले से सीखे अभ्यास पर क्या प्रभाव पड़ता है।'),
    (40.0, 'उद्देश्य अपने लिए कठोर नियम बनाना नहीं है। उद्देश्य है—बार-बार दिखाई देने वाले व्यक्तिगत ढंग को ईमानदारी से पहचानना।'),

    (58.0, 'सबसे पहले आज की स्थिति का छोटा आधार-अभिलेख बनाएँ।'),
    (67.0, 'लिखें—आज शरीर में ऊर्जा कैसी है, थकान कितनी है, मनोदशा कैसी है, और पिछली प्रमुख गतिविधि क्या थी।'),
    (88.0, 'फिर पहले सीखे हुए छोटे क्रम से मूल स्पर्श-बिन्दु को जानें और लिखें कि वह कितनी देर में स्पष्ट हुआ।'),
    (103.0, 'हर तुलना में अभ्यास का मूल क्रम वही रखें। तभी पहले और बाद का अन्तर अर्थपूर्ण होगा।'),

    (118.0, 'अब उन सेवनों को समझें जो बार-बार संवेदनशीलता घटाते दिखाई दे सकते हैं।'),
    (128.0, 'स्रोत मदिरा से बचने और उस तामसिक या अति-मसालेदार सेवन को घटाने का सुझाव देता है, जो आपके अभिलेख में बार-बार स्पष्टता कम करता दिखे।'),
    (151.0, 'किसी सेवन को जानबूझकर लेकर परीक्षण न करें। जीवन में जो स्थिति स्वाभाविक रूप से आए, केवल उसी का पहले और बाद का प्रभाव लिखें।'),

    (169.0, 'योगासन को सहायक साधन की तरह देखा जा सकता है।'),
    (177.0, 'यह पाठ कोई नया आसन नहीं सिखा रहा। अपने शिक्षक से स्वीकृत या पहले से सुरक्षित रूप से सीखे योगासन का ही उपयोग करें।'),
    (194.0, 'जहाँ व्यावहारिक हो, सुबह या शाम के अभ्यास से पहले और बाद में मूल स्पर्श-बिन्दु की स्पष्टता की तुलना करें।'),
    (213.0, 'योगासन का प्रकार, अवधि, शरीर की स्थिति और अनुभव स्पष्ट होने में लगा समय लिखें।'),

    (229.0, 'प्रकृति में बिताया समय भी एक सहायक विकल्प है।'),
    (238.0, 'स्रोत मिट्टी या घास पर लगभग तीस मिनट नंगे पैर चलने को एक विकल्प बताता है।'),
    (252.0, 'यह केवल सुरक्षित, साफ और चोट से मुक्त स्थान पर करें। असुरक्षित भूमि पर नंगे पैर न चलें।'),
    (269.0, 'प्रकृति में जाने से पहले और लौटने के बाद ऊर्जा, मनोदशा और मूल स्पर्श-बिन्दु की स्पष्टता लिखें।'),

    (287.0, 'अब अधिक परिश्रम के प्रभाव को देखें।'),
    (295.0, 'गर्मी में अधिक दौड़ना, थकाऊ यात्रा, अनावश्यक काम या लगातार शरीर को खाली कर देने वाली गतिविधि के बाद अनुभव बदल सकता है।'),
    (317.0, 'गतिविधि, थकान की मात्रा और बाद में स्पर्श-बिन्दु स्पष्ट होने में लगा समय दर्ज करें।'),
    (333.0, 'दर्द, चक्कर या अत्यधिक थकान के बीच अभ्यास को बलपूर्वक जारी न रखें। पहले शरीर को सुरक्षित आराम दें।'),

    (351.0, 'अब क्रोध के समय और बाद के परिवर्तन का निरीक्षण करें।'),
    (360.0, 'लिखें—क्रोध का कारण क्या था, उसकी तीव्रता कितनी थी, और मूल स्पर्श-बिन्दु की स्पष्टता पर क्या असर पड़ा।'),
    (380.0, 'स्थिति शांत होने पर वही छोटा अभ्यास दोहराएँ और लिखें कि स्पष्टता लौटने में कितना समय लगा।'),
    (398.0, 'क्रोध को जोर से दबाना इस निरीक्षण का उद्देश्य नहीं है। परिस्थिति संभालें, फिर बिना निर्णय के प्रभाव को जानें।'),

    (418.0, 'यौन गतिविधि या चरमसुख के बाद भी जीवंतता और संवेदनशीलता का व्यक्तिगत निरीक्षण किया जा सकता है।'),
    (433.0, 'इसे शर्म, अपराधबोध या नैतिक निर्णय का विषय न बनाएँ। केवल समय, तीव्रता और सामान्य स्थिति लौटने में लगा समय दर्ज करें।'),
    (454.0, 'परीक्षण के लिए गतिविधि को जानबूझकर दोहराना आवश्यक नहीं है। जीवन में स्वाभाविक रूप से होने वाली स्थिति का ही निरीक्षण करें।'),
    (473.0, 'किसी बदलाव को बलपूर्वक दबाने के बजाय, समझ और बार-बार दिखने वाले अनुभव के आधार पर अपनी प्रतिक्रिया विकसित करें।'),

    (493.0, 'अब आचरण के प्रभाव को देखें।'),
    (501.0, 'ईमानदारी, निष्ठा, अहिंसा, प्रेमपूर्ण व्यवहार, दान और सेवा के बाद अपने भीतर की स्थिति को जानें।'),
    (519.0, 'क्या मूल स्पर्श-बिन्दु अधिक स्पष्ट हुआ, कम हुआ, या कोई दोहरता हुआ अन्तर दिखाई नहीं दिया—जो सत्य हो, वही लिखें।'),
    (538.0, 'एक घटना से निष्कर्ष न निकालें। अलग-अलग अवसरों पर वही संबंध दोहरता है या नहीं, यह देखें।'),

    (555.0, 'अब आप मेरे साथ अपना निरीक्षण-कार्य चुनें।'),
    (564.0, 'एक सहायक कारक चुनें—जैसे योगासन, प्रकृति में समय या सेवा।'),
    (577.0, 'फिर एक ऐसा कारक चुनें, जिसके बाद आपके अनुभव में कमी आने की सम्भावना आपने पहले देखी हो—जैसे अधिक थकान, क्रोध या कोई विशेष सेवन।'),
    (599.0, 'किसी हानिकारक स्थिति को जानबूझकर पैदा नहीं करना है। केवल स्वाभाविक अवसर आने पर उसका निरीक्षण करना है।'),
    (616.0, 'अपनी नोटबुक में दो खण्ड बनाएँ—पहले और बाद में।'),
    (628.0, 'दोनों खण्डों में लिखें—तारीख, समय, चुना हुआ कारक, ऊर्जा, थकान, मनोदशा, अनुभव स्पष्ट होने का समय और अनुभव की गुणवत्ता।'),
    (652.0, 'अगले पच्चीस सेकंड में अपना पहला निरीक्षण-कार्य और उसे करने का सम्भावित दिन लिखें।'),

    (678.0, 'अन्तिम जाँच करें। क्या आपने कोई अस्वास्थ्यकर स्थिति जानबूझकर नहीं चुनी? क्या दोनों बार मूल अभ्यास वही रहेगा? क्या आप एक घटना के बजाय दोहरते ढंग को देखेंगे? यही पाठ सात का कार्य है।'),
]

async def synth(text: str, out_mp3: Path) -> None:
    comm = edge_tts.Communicate(text, VOICE, rate='-4%', pitch='+0Hz', volume='+0%')
    await comm.save(str(out_mp3))

def trim(seg: AudioSegment) -> AudioSegment:
    if seg.dBFS == float('-inf'):
        return seg
    ranges = detect_nonsilent(seg, min_silence_len=70, silence_thresh=max(-47, seg.dBFS - 28), seek_step=5)
    if not ranges:
        return seg
    a = max(0, ranges[0][0] - 80)
    b = min(len(seg), ranges[-1][1] + 130)
    return seg[a:b]

def atempo_chain(factor: float) -> str:
    parts = []
    while factor > 2.0:
        parts.append(2.0); factor /= 2.0
    while factor < 0.5:
        parts.append(0.5); factor /= 0.5
    parts.append(factor)
    return ','.join(f'atempo={x:.6f}' for x in parts)

def fit(seg: AudioSegment, max_ms: int, idx: int) -> AudioSegment:
    if len(seg) <= max_ms:
        return seg
    factor = len(seg) / max_ms
    src = TMP / f'fit_{idx:02d}_src.wav'
    dst = TMP / f'fit_{idx:02d}_dst.wav'
    seg.export(src, format='wav')
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),
        '-filter:a',atempo_chain(factor),'-ar','48000','-ac','1',str(dst)
    ], check=True)
    return AudioSegment.from_wav(dst)

def srt_time(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3_600_000); m, ms = divmod(ms, 60_000); s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

async def main() -> None:
    master = AudioSegment.silent(duration=TOTAL_MS, frame_rate=48000).set_channels(1)
    meta, srt, script_lines = [], [], []
    for i, (start, text) in enumerate(CUES, 1):
        mp3 = TMP / f'{i:02d}.mp3'
        await synth(text, mp3)
        seg = trim(AudioSegment.from_file(mp3)).set_frame_rate(48000).set_channels(1)
        if seg.dBFS != float('-inf'):
            seg = seg.apply_gain(TARGET_DBFS - seg.dBFS)
        next_start = CUES[i][0] if i < len(CUES) else TOTAL_MS / 1000
        max_ms = max(900, int((next_start - start) * 1000) - 260)
        seg = fit(seg, max_ms, i)
        wav = CUE_DIR / f'{i:02d}.wav'
        seg.export(wav, format='wav')
        master = master.overlay(seg, position=int(start * 1000))
        end = min(TOTAL_MS / 1000, start + len(seg) / 1000)
        meta.append({'start': start, 'end': end, 'text': text, 'audio': wav.name})
        srt.extend([str(i), f'{srt_time(start)} --> {srt_time(end)}', text, ''])
        script_lines.append(text)

    wav_master = ROOT / 'Vishranti_Bindu_Video7_Hindi_Narration.wav'
    m4a_master = ROOT / 'Vishranti_Bindu_Video7_Hindi_Narration.m4a'
    master.export(wav_master, format='wav')
    subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav_master),
        '-af','highpass=f=70,lowpass=f=12000,alimiter=limit=0.94',
        '-t',str(TOTAL_MS/1000),'-c:a','aac','-b:a','224k','-ar','48000','-ac','2',str(m4a_master)
    ], check=True)
    (ROOT / 'cues.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'Vishranti_Bindu_Video7_Hindi_Subtitles.srt').write_text('\n'.join(srt), encoding='utf-8')
    (ROOT / 'Vishranti_Bindu_Video7_Hindi_Voiceover_Script.txt').write_text('\n\n'.join(script_lines), encoding='utf-8')
    (ROOT / 'README.txt').write_text('VB Video 7 Hindi narration and subtitles. Duration: 11:30. Voice: hi-IN-SwaraNeural.', encoding='utf-8')

asyncio.run(main())
