const fs = require('fs');
const path = require('path');

// Carga dinámica de node-fetch para compatibilidad con ESM/CommonJS en Node 18+
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const CONFIG = {
  guacharo: {
    apiUrl: 'https://api.lotterly.co/v1/results/guacharo-activo/',
    numeros: 12,
    nombre: 'Guácharo Activo',
    procesar: async (fecha) => {
      const fechaStr = fecha.toISOString().split('T')[0];
      const url = `${CONFIG.guacharo.apiUrl}?exact_date=${fechaStr}&extended=true&_t=${Date.now()}`;
      try {
        const response = await fetch(url, { headers: { 'User-Agent': 'DrAnimalitosBot/1.0' } });
        if (!response.ok) return null;
        const data = await response.json();
        if (Array.isArray(data) && data.length === 12) {
          return data.map(sorteo => {
            const res = sorteo.results?.[0]?.result;
            return res === "00" ? "00" : parseInt(res);
          });
        }
      } catch (e) { return null; }
      return null;
    }
  },
  granja: {
    apiUrl: 'http://www.granjamillonaria.com/Resource?a=granja-millonaria-lista',
    numeros: 10,
    nombre: 'Granja Millonaria',
    procesar: async (fecha) => {
      const fechaStr = `${String(fecha.getDate()).padStart(2, '0')}/${String(fecha.getMonth() + 1).padStart(2, '0')}/${fecha.getFullYear()}`;
      try {
        const response = await fetch(CONFIG.granja.apiUrl);
        if (!response.ok) return null;
        const data = await response.json();
        const diaData = data.find(d => d.fecha === fechaStr);
        if (!diaData || !diaData.rss) return null;
        const nums = diaData.rss.filter(i => i.nu).map(i => parseInt(i.nu)).slice(0, 10);
        return nums.length === 10 ? nums : null;
      } catch (e) { return null; }
    }
  },
  granjazo: {
    apiUrl: 'http://www.granjamillonaria.com/Resource?a=granja-millonaria-lista',
    numeros: 10,
    nombre: 'Granjazo Millonario',
    procesar: async (fecha) => {
      const fechaStr = `${String(fecha.getDate()).padStart(2, '0')}/${String(fecha.getMonth() + 1).padStart(2, '0')}/${fecha.getFullYear()}`;
      try {
        const response = await fetch(CONFIG.granjazo.apiUrl);
        if (!response.ok) return null;
        const data = await response.json();
        const diaData = data.find(d => d.fecha === fechaStr);
        if (!diaData || !diaData.rsj) return null;
        const nums = diaData.rsj.filter(i => i.nu).map(i => parseInt(i.nu)).slice(0, 10);
        return nums.length === 10 ? nums : null;
      } catch (e) { return null; }
    }
  },
  lotto: {
    apiUrl: 'https://lottoactivo.com/core/process.php',
    numeros: 12,
    nombre: 'Lotto Activo',
    procesar: async (fecha) => {
      const fechaStr = fecha.toISOString().split('T')[0];
      const formData = new URLSearchParams();
      formData.append('option', 'WDNxcnFwcnNPb1lrd3VTSXEyYll0USRMNFJSNm50dzBHbTZxd1d3VjI4b0ZvVEY4djEyNElpNWpIenpsTWlqY1pKdENLT2E4dlZpaWV1SXk3WThTMkZmMVl6WUZudXNFMTcrUzJYMmhiL0xOQT09');
      formData.append('loteria', 'lotto_activo');
      formData.append('fecha', fechaStr);
      try {
        const response = await fetch(CONFIG.lotto.apiUrl, { method: 'POST', body: formData });
        if (!response.ok) return null;
        const data = await response.json();
        if (!data.datos) return null;
        const orden = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00'];
        const nums = data.datos
          .sort((a, b) => orden.indexOf(a.time_s.replace(/am|pm/g, '').trim()) - orden.indexOf(b.time_s.replace(/am|pm/g, '').trim()))
          .map(i => i.number_animal === "00" ? "00" : parseInt(i.number_animal));
        return nums.length === 12 ? nums : null;
      } catch (e) { return null; }
    }
  }
};

async function actualizarJSON(loteria, nuevosNumeros) {
  const ruta = path.join(__dirname, `../data/${loteria}.json`);
  if (!fs.existsSync(ruta)) {
    console.log(`❌ Archivo no encontrado: ${ruta}`);
    return false;
  }
  const actual = JSON.parse(fs.readFileSync(ruta, 'utf8'));
  const [diaViejo, diaMedio, diaReciente] = actual.resultados;
  
  // Rotación: el medio pasa a viejo, el reciente a medio, y el nuevo a reciente
  actual.resultados = [diaMedio, diaReciente, nuevosNumeros];
  actual.fecha_actualizacion = new Date().toISOString();
  
  fs.writeFileSync(ruta, JSON.stringify(actual, null, 2));
  console.log(`✅ ${loteria}.json actualizado.`);
  return true;
}

async function main() {
  const loterias = ['guacharo', 'granja', 'granjazo', 'lotto'];
  for (const loteria of loterias) {
    let nums = null;
    // Intenta hoy, ayer y anteayer
    for (let i = 0; i <= 2; i++) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      // Ajuste básico a hora Venezuela (UTC-4)
      const fechaVzla = new Date(d.getTime() - (4 * 60 * 60 * 1000));
      console.log(`🔍 Buscando ${CONFIG[loteria].nombre} para fecha: ${fechaVzla.toISOString().split('T')[0]}`);
      nums = await CONFIG[loteria].procesar(fechaVzla);
      if (nums) break;
    }
    if (nums) {
      await actualizarJSON(loteria, nums);
    } else {
      console.log(`⚠️ No se obtuvieron resultados para ${loteria}`);
    }
  }
}

main().catch(console.error);
