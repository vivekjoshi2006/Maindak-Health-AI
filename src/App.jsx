import React, { useState } from 'react';
import axios from 'axios';
import html2pdf from 'html2pdf.js';
import './App.css';


function App() {


  // ---------------------------------------------- STATE MANAGEMENT ----------------------------------------------

  const [input, setInput] = useState('');                     // Input query
  const [result, setResult] = useState(null);                 // Result data
  const [loading, setLoading] = useState(false);              // Loading state for API calls
  const [darkMode, setDarkMode] = useState(false);            // Theme
  const [type, setType] = useState('disease');                // Search category (disease/medicine)
  const [showFollowup, setShowFollowup] = useState(false);    // Follow-up question toggle
  const [showAbout, setShowAbout] = useState(false);          // About modal toggle



  // ---------------------------------------------- LOGIC HANDLERS ----------------------------------------------

  // Fetches health data from the Flask Backend

  const performSearch = async (queryInput) => {
    if (!queryInput.trim()) return;
    setLoading(true);
    setResult(null);
    setShowFollowup(false);


    try {
      const res = await axios.post("/api/chatbot/ask", {
        message: queryInput,
        type: type
      });
      setResult(res.data);
    } catch (err) {
      setResult({ error: "Froggy is jumping around! 🐸" });
    } finally {
      setLoading(false);
    }
  };



  // --------------------------------GENERATE AND DOWNLOAD THE REPORT --------------------------------

  const downloadPDF = () => {
    const element = document.getElementById('report-card-capture');
    const followupSection = document.querySelector('.froggy-followup-box');


    // UI Cleanup for PDF

    if (followupSection) followupSection.style.display = 'none';

    const opt = {
      margin: 10,
      filename: `Maindak_Report_${Date.now()}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(element).save().then(() => {
      if (followupSection) followupSection.style.display = 'block';
    });
  };



  //------------------------------------------- TRANSLATE WIDGET -------------------------------------------

  const handleTranslate = () => {
    const translateElement = document.getElementById('google_translate_element');
    if (translateElement) {
      translateElement.style.display = 'block';
      const selectBox = translateElement.querySelector('select');
      if (selectBox) {
        selectBox.focus();
      } else {
        alert("Froggy is loading the translator... 🐸");
      }
    }
  };



  // --------------------------------------------- RENDER UI -------------------------------------------------------

  return (
    <div className={`maindak-container ${darkMode ? 'dark' : 'light'}`}>


      {/* 🌌 COSMIC FLUID MESH GRADIENT */}

      <div className="mesh-gradient">
        <div className="mesh-ball ball-1"></div>
        <div className="mesh-ball ball-2"></div>
        <div className="mesh-ball ball-3"></div>
        <div className="mesh-ball ball-4"></div>
      </div>


      {!result ? (
        <div className="home-screen">


          {/* Top Navbar Actions */}

          <div className="top-actions-home">


            {/* LHS: Froggy Button */}

            <button className="about-toggle-btn-lhs" onClick={() => setShowAbout(true)}>
              <span>🐸</span>
            </button>


            {/* RHS: Theme Toggle */}

            <button className="theme-toggle-icon" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? '☀️' : '🌙'}
            </button>


            {/* About Modal Overlay */}

            {showAbout && (
              <div className="about-modal-overlay" onClick={() => setShowAbout(false)}>
                <div className="about-card-popup" onClick={(e) => e.stopPropagation()}>
                  <div className="about-content">
                    <span className="frog-head-large">🐸</span>
                    <h2 className="about-title-main">Maindak AI</h2>


                    {/* Info Section */}

                    <div className="about-interactive-info">
                      <div className="info-line">
                        <span className="info-emoji">🌟</span>
                        <p>Get instant, AI-powered health guidance for all your queries.</p>
                      </div>
                      <div className="info-line">
                        <span className="info-emoji">🛡️</span>
                        <p>Access verified medical precautions and essential care tips.</p>
                      </div>
                      <div className="info-line">
                        <span className="info-emoji">⚡</span>
                        <p>Experience fast, smart, and interactive medical assistance.</p>
                      </div>
                    </div>


                    <hr className="about-divider-glow" />
                    <span className="credit-label-text">CREATED BY</span>
                    <h1 className="creator-name-mega">VIVEK JOSHI</h1>


                    {/* Social */}

                    <div className="contact-dock">
                      <a href="mailto:vivekjoshi41996@gmail.com" className="social-icon-btn" title="Email">📧</a>
                      <a href="https://www.linkedin.com/in/vivekjoshi2006" target="_blank" rel="noreferrer" className="social-icon-btn" title="LinkedIn">🔗</a>
                      <span className="guard-snake-mega">🐍</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>


          {/* Central Section */}

          <div className="hero">
            <div className="frog-icon">🐸</div>
            <h1 className="title">Maindak</h1>
            <p className="tagline">Your Health AI 🩺</p>
            <p className="welcome-text">Hi! I'm Froggy 🐸 How can I help you?</p>
          </div>


          {/* Search Category */}

          <div className="category-grid">
            {['disease', 'medicine'].map(cat => (
              <button
                key={cat}
                className={type === cat ? 'active' : ''}
                onClick={() => setType(cat)}
              >
                {cat === 'disease' ? '🤒 Disease' : '💊 Medicine'}
              </button>
            ))}
          </div>


          {/* Main Search Bar */}

          <form className="search-form" onSubmit={(e) => { e.preventDefault(); performSearch(input); }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Search for ${type}...`}
            />
            <button type="submit">{loading ? "Searching...🐸" : "Ask Froggy"}</button>
          </form>
        </div>
      ) : (



        /* CASE B: RESULT VIEW (After API Response) */

        <div className="result-view">


          {/* Sidebar Floating Actions (LHS & RHS) */}

          <div className="side-actions left-side">
            <button className="icon-btn theme" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? '☀️' : '🌙'} <span>Theme</span>
            </button>
            <button className="icon-btn translate" onClick={handleTranslate}>
              🌐 <span>Translate</span>
            </button>
          </div>


          {/* RHS Floating Actions */}

          <div className="side-actions right-side">
            <button className="icon-btn pdf" onClick={downloadPDF}>
              📥 <span>Download</span>
            </button>
            <button className="icon-btn back" onClick={() => { setResult(null); setInput(''); }}>
              🔙 <span>Back</span>
            </button>
          </div>


          {/* Printable Report Card */}

          <div id="report-card-capture" className="report-card">
            <h1 className="report-heading">Analysis Result: {result.name || "HEALTH REPORT"}</h1>

            <div className="report-grid">
              {type === 'disease' ? (
                <>

                  {/* Disease Specific Content */}

                  <div className="info-box care-box">
                    <h2 className="box-heading">🛡️ Care & Precautions</h2>
                    <div className="box-content">
                      {result.details?.map((d, i) => (
                        <div key={i} className="point-item">
                          <span>✦</span> {d}
                        </div>
                      ))}
                    </div>
                  </div>


                  <div className="info-box medicine-box">
                    <h2 className="box-heading">💊 Suggested Medicines</h2>
                    <div className="box-content">


                      {/* Medicines list*/}

                      {result.medicines?.map((med, i) => (
                        <div key={i} className="point-item">
                          <span>✦</span> {med}
                        </div>
                      ))}


                      {/* 🆕 Disclaimer Box */}

                      <div className="single-disclaimer-box">
                        <span className="warning-icon">⚠️</span>
                        <p>
                          <strong>Medical Disclaimer:</strong> Information is for educational purposes only.
                          Always consult a healthcare professional before taking any medication.
                        </p>
                      </div>
                    </div>
                  </div>
                </>
              ) : (


                /* Medicine Specific Content */

                <div className="info-box uses-box">
                  <h2 className="box-heading">📋 USES</h2>
                  <div className="box-content">
                    {result.details?.map((d, i) => (
                      <div key={i} className="point-item">
                        <span>✦</span> {d}
                      </div>
                    ))}
                  </div>
                </div>
              )}


              {/* Resources Section */}

              <div className="info-box resources-box">
                <h2 className="box-heading">📚 Verified Resources</h2>
                <div className="box-content">
                  <div className="resource-list-vertical">
                    {result.links?.map((l, i) => (
                      <div key={i} className="resource-item-vertical">
                        <span className="bullet-icon">📍</span>
                        <a href={l.url} target="_blank" rel="noreferrer" className="res-link">
                          {l.title} ↗
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>


            {/* Follow-up Section */}

            <div className="froggy-followup-box">
              {!showFollowup ? (
                <>
                  <h2 className="followup-heading-large">Would you like to ask anything else? 🐸</h2>
                  <div className="btn-group">
                    <button className="interactive-btn yes" onClick={() => setShowFollowup(true)}>Yes, please! ✨</button>
                    <button className="interactive-btn no" onClick={() => { setResult(null); setInput(''); }}>No, I'm good. 👍</button>
                  </div>
                </>
              ) : (
                <div className="followup-active-area">
                  <p className="followup-new-line">I'm listening! What's on your mind? 🌸</p>
                  <form className="search-form" onSubmit={(e) => { e.preventDefault(); performSearch(input); }}>
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Type your next question here..."
                      autoFocus
                    />
                    <button type="submit">Ask</button>
                  </form>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
