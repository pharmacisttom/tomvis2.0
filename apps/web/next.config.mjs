const backend = new URL(process.env.TOMVIS_API_URL || 'http://127.0.0.1:8000');
if (backend.protocol !== 'http:' || !['localhost','127.0.0.1'].includes(backend.hostname) || backend.username || backend.password || backend.pathname !== '/' || backend.search || backend.hash) throw Error('Local FastAPI origin required in this alpha');
export default {
  poweredByHeader: false,
  async headers() {return [{source:'/:path*',headers:[{key:'X-Content-Type-Options',value:'nosniff'},{key:'X-Frame-Options',value:'DENY'},{key:'Referrer-Policy',value:'no-referrer'}]}];},
};
