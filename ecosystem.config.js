module.exports = {
  apps: [
    {
      name: "aetherix-backend",
      cwd: "./backend",
      script: "run.py",
      interpreter: "python3",
      env: {
        DATABASE_URL: "sqlite:///./aetherix.db",
        BACKEND_PORT: 8000,
        DEBUG: "true",
      },
      watch: false,
      max_restarts: 5,
      restart_delay: 3000,
    },
    {
      name: "aetherix-frontend",
      cwd: "./frontend",
      script: "node_modules/.bin/vite",
      env: {
        PORT: 3000,
        VITE_API_URL: "/api",
      },
      watch: false,
      max_restarts: 5,
      restart_delay: 3000,
    },
  ],
};
