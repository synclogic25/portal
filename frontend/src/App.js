import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, [token]);

  const checkAuth = async () => {
    try {
      const response = await axios.get(`${API}/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/login`, { username, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        message: error.response?.data?.detail || 'Erreur de connexion' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, token }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(credentials.username, credentials.password);
    
    if (!result.success) {
      setError(result.message);
    }
    
    setLoading(false);
  };

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md transform transition-all duration-300 hover:scale-105">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-6">
            <img 
              src="data:image/png;base64,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" 
              alt="SyncLogic" 
              className="h-12 w-auto"
              onError={(e) => {
                // Fallback to SVG icon if image fails to load
                e.target.style.display = 'none';
                e.target.nextElementSibling.style.display = 'block';
              }}
            />
            <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-4 rounded-xl" style={{display: 'none'}}>
              <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
            </div>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
            SyncLogic
          </h1>
          <p className="text-gray-600 mt-2">Portail Client</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom d'utilisateur
            </label>
            <input
              type="text"
              name="username"
              value={credentials.username}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200"
              placeholder="Votre nom d'utilisateur"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              type="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition-all duration-200"
              placeholder="Votre mot de passe"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-cyan-600 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:ring-offset-2 transform transition-all duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          Compte de test: <span className="font-medium">admin / password</span>
        </div>
      </div>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout, token } = useAuth();

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      const response = await axios.get(`${API}/applications`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setApplications(response.data);
    } catch (error) {
      console.error('Error fetching applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAppClick = async (app) => {
    if (app.category === 'native') {
      // For native apps, redirect to the URL
      if (app.url) {
        window.open(app.url, '_blank');
      }
    } else {
      // For portal apps, generate token
      try {
        const response = await axios.post(
          `${API}/applications/${app.id}/access-token`,
          {},
          { headers: { Authorization: `Bearer ${token}` } }
        );
        console.log('Generated token for', app.name, ':', response.data.access_token);
        // In a real implementation, you would redirect with this token
        alert(`Token généré pour ${app.name}: ${response.data.access_token}`);
      } catch (error) {
        console.error('Error generating token:', error);
      }
    }
  };

  const nativeApps = applications.filter(app => app.category === 'native');
  const portalApps = applications.filter(app => app.category === 'portal');

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <img 
                src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAALQAAAAnCAYAAACVGOJuAAAACXBIWXMAAAsSAAALEgHS3X78AAANfElEQVR4nO2dfXQc1XnGfzN7kVZf1tqSbdmyvpJlW5ZlW7LkhxjbYDAEG4iBQCiQD0ggDWkD5ISEtJAeTnKapj2n/bdt2gQCaZoQCKFJIAGbOODEH5K/ZH/Ikm1JlmVbX5Zl7e7szD/emdmdnZnZ2V1pJcv33HPOzs7u3Lnzvs+9731/974jABYvXox58+YhLy8PUqkU\..." 
                alt="SyncLogic" 
                className="h-8 w-auto mr-3"
                onError={(e) => {
                  // Fallback to SVG icon if image fails to load
                  e.target.style.display = 'none';
                  e.target.nextElementSibling.style.display = 'block';
                }}
              />
              <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-2 rounded-lg mr-3" style={{display: 'none'}}>
                <svg className="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                  <path d="M2 17L12 22L22 17"/>
                  <path d="M2 12L12 17L22 12"/>
                </svg>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                SyncLogic Portal
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Bonjour, {user?.full_name || user?.username}</span>
              <button
                onClick={logout}
                className="bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-lg hover:from-red-600 hover:to-red-700 transition-all duration-200 transform hover:scale-105"
              >
                Déconnexion
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Native Apps Section */}
        <section className="mb-12">
          <div className="flex items-center mb-6">
            <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-600 rounded-full mr-4"></div>
            <h2 className="text-2xl font-bold text-gray-800">Applications avec Accès Sécurisé Natif</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {nativeApps.map(app => (
              <div
                key={app.id}
                onClick={() => handleAppClick(app)}
                className="bg-white rounded-xl shadow-lg hover:shadow-2xl transform transition-all duration-300 hover:scale-105 cursor-pointer group overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-400 to-blue-600 rounded-xl mb-4 text-2xl text-white group-hover:from-blue-500 group-hover:to-blue-700 transition-all duration-300">
                    {app.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">{app.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{app.description}</p>
                  <div className="flex items-center text-xs text-blue-600 font-medium">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                    Accès Direct
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Portal Apps Section */}
        <section>
          <div className="flex items-center mb-6">
            <div className="h-8 w-1 bg-gradient-to-b from-purple-500 to-indigo-600 rounded-full mr-4"></div>
            <h2 className="text-2xl font-bold text-gray-800">Applications Sécurisées par le Portail</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {portalApps.map(app => (
              <div
                key={app.id}
                onClick={() => handleAppClick(app)}
                className="bg-white rounded-xl shadow-lg hover:shadow-2xl transform transition-all duration-300 hover:scale-105 cursor-pointer group overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-400 to-indigo-600 rounded-xl mb-4 text-2xl text-white group-hover:from-purple-500 group-hover:to-indigo-700 transition-all duration-300">
                    {app.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">{app.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{app.description}</p>
                  <div className="flex items-center text-xs text-purple-600 font-medium">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                    Token Requis
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

const AppContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    );
  }

  return user ? <Dashboard /> : <Login />;
};

export default App;