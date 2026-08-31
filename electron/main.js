const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');

const store = new Store();
let mainWindow;
let djangoProcess;

// Configuration
const DJANGO_PORT = 8000;
const DJANGO_HOST = '127.0.0.1';
const DJANGO_URL = `http://${DJANGO_HOST}:${DJANGO_PORT}`;

function createWindow() {
  // Créer la fenêtre du navigateur
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 768,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false
    },
    show: false, // Ne pas afficher tant que le serveur n'est pas prêt
    backgroundColor: '#ffffff'
  });

  // Menu personnalisé
  const template = [
    {
      label: 'Fichier',
      submenu: [
        {
          label: 'Actualiser',
          accelerator: 'F5',
          click: () => {
            mainWindow.reload();
          }
        },
        { type: 'separator' },
        {
          label: 'Quitter',
          accelerator: 'Alt+F4',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Affichage',
      submenu: [
        {
          label: 'Plein écran',
          accelerator: 'F11',
          click: () => {
            mainWindow.setFullScreen(!mainWindow.isFullScreen());
          }
        },
        { type: 'separator' },
        {
          label: 'Outils de développement',
          accelerator: 'F12',
          click: () => {
            mainWindow.webContents.toggleDevTools();
          }
        }
      ]
    },
    {
      label: 'Aide',
      submenu: [
        {
          label: 'À propos',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'À propos',
              message: 'Biantos Agency v1.0.0',
              detail: 'Application de gestion de commandes\n\n© 2024 Biantos'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);

  // Écran de chargement
  mainWindow.loadFile(path.join(__dirname, 'loading.html'));
  mainWindow.show();

  // Démarrer Django
  startDjango();
}

function startDjango() {
  console.log('🚀 Démarrage du serveur Django...');

  // Chemin vers les ressources de l'application
  const resourcesPath = process.resourcesPath || app.getAppPath();
  const appPath = path.join(resourcesPath, 'app');
  
  // Déterminer le chemin de Python
  const pythonPath = process.platform === 'win32' 
    ? path.join(appPath, 'venv', 'Scripts', 'python.exe')
    : path.join(appPath, 'venv', 'bin', 'python');

  // Commande pour démarrer Django
  const managePath = path.join(appPath, 'manage.py');
  
  djangoProcess = spawn(pythonPath, [
    managePath,
    'runserver',
    `${DJANGO_HOST}:${DJANGO_PORT}`,
    '--noreload'
  ], {
    cwd: appPath,
    env: { ...process.env, PYTHONUNBUFFERED: '1' }
  });

  djangoProcess.stdout.on('data', (data) => {
    console.log(`Django: ${data}`);
    
    // Vérifier si le serveur est prêt
    if (data.toString().includes('Starting development server')) {
      setTimeout(() => {
        console.log('✅ Serveur Django prêt');
        mainWindow.loadURL(DJANGO_URL);
      }, 1000);
    }
  });

  djangoProcess.stderr.on('data', (data) => {
    console.error(`Django Error: ${data}`);
  });

  djangoProcess.on('close', (code) => {
    console.log(`Django process exited with code ${code}`);
  });
}

function stopDjango() {
  if (djangoProcess) {
    console.log('🛑 Arrêt du serveur Django...');
    djangoProcess.kill();
    djangoProcess = null;
  }
}

// Quand Electron a fini de s'initialiser
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quitter quand toutes les fenêtres sont fermées
app.on('window-all-closed', () => {
  stopDjango();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Arrêter Django avant de quitter
app.on('before-quit', () => {
  stopDjango();
});

// Gérer les erreurs non capturées
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
});
