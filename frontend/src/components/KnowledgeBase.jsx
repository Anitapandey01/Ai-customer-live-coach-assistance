import { useEffect, useState } from "react";

function KnowledgeBase({ user, onBack }) {
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [documentName, setDocumentName] = useState("");
  const [documentType, setDocumentType] = useState("faq");

  const [selectedDocument, setSelectedDocument] = useState(null);
  const [history, setHistory] = useState([]);

  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const token = user?.access_token;

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/documents/",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to load documents."
        );
      }

      setDocuments(data.documents || []);
    } catch (error) {
      setError(
        error.message || "Unable to load documents."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (
      user?.role === "admin" ||
      user?.role === "employee"
    ) {
      fetchDocuments();
    }
  }, [user]);

  const handleUpload = async (event) => {
    event.preventDefault();

    setError("");
    setSuccess("");

    if (!file) {
      setError("Please select a PDF file.");
      return;
    }

    if (!documentName.trim()) {
      setError("Please enter a document name.");
      return;
    }

    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed.");
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();

      formData.append("file", file);
      formData.append(
        "document_name",
        documentName.trim()
      );
      formData.append(
        "document_type",
        documentType
      );

      const response = await fetch(
        "http://127.0.0.1:8000/documents/upload",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Document upload failed."
        );
      }

      setSuccess(
        "Document uploaded and processed successfully."
      );

      setFile(null);
      setDocumentName("");
      setDocumentType("faq");

      const fileInput =
        document.getElementById("document-file");

      if (fileInput) {
        fileInput.value = "";
      }

      await fetchDocuments();
    } catch (error) {
      setError(
        error.message || "Document upload failed."
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleViewHistory = async (documentName) => {
    setError("");
    setSelectedDocument(documentName);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/documents/history/${encodeURIComponent(
          documentName
        )}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Unable to load version history."
        );
      }

      setHistory(data.versions || []);
    } catch (error) {
      setError(
        error.message ||
          "Unable to load version history."
      );
    }
  };

  if (
    user?.role !== "admin" &&
    user?.role !== "employee"
  ) {
    return (
      <div className="mode-container">
        <h2>Access Denied</h2>

        <p>
          You do not have permission to access the
          Knowledge Base.
        </p>

        <button
          type="button"
          className="secondary-button"
          onClick={onBack}
        >
          Back
        </button>
      </div>
    );
  }

  return (
    <div className="mode-container">
      <div className="mode-header">
        <div>
          <h2>Knowledge Base</h2>

          <p>
            Manage and review support documents.
          </p>
        </div>

        <button
          type="button"
          className="secondary-button"
          onClick={onBack}
        >
          Back
        </button>
      </div>

      {error && (
        <p className="login-error">
          {error}
        </p>
      )}

      {success && (
        <p className="login-success">
          {success}
        </p>
      )}

      {user?.role === "admin" && (
        <div className="user-form-card">
          <h3>Upload Support Document</h3>

          <form onSubmit={handleUpload}>
            <div className="form-group">
              <label htmlFor="document-name">
                Document Name
              </label>

              <input
                id="document-name"
                type="text"
                placeholder="e.g. Refund Policy"
                value={documentName}
                onChange={(event) =>
                  setDocumentName(
                    event.target.value
                  )
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="document-type">
                Document Type
              </label>

              <select
                id="document-type"
                value={documentType}
                onChange={(event) =>
                  setDocumentType(
                    event.target.value
                  )
                }
              >
                <option value="faq">FAQ</option>
                <option value="policy">Policy</option>
                <option value="support">
                  Support
                </option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="document-file">
                PDF File
              </label>

              <input
                id="document-file"
                type="file"
                accept="application/pdf"
                onChange={(event) =>
                  setFile(
                    event.target.files[0] || null
                  )
                }
              />
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={isUploading}
            >
              {isUploading
                ? "Uploading..."
                : "Upload Document"}
            </button>
          </form>
        </div>
      )}

      <div className="users-list-card">
        <div className="mode-header">
          <div>
            <h3>Support Documents</h3>

            <p>
              {documents.length} document version
              {documents.length !== 1
                ? "s"
                : ""}
            </p>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={fetchDocuments}
            disabled={isLoading}
          >
            {isLoading
              ? "Loading..."
              : "Refresh"}
          </button>
        </div>

        {documents.length === 0 &&
        !isLoading ? (
          <p>No documents found.</p>
        ) : (
          <div className="users-list">
            {documents.map((document) => (
              <div
                key={document.document_id}
                className="user-row"
              >
                <div>
                  <strong>
                    {document.document_name}
                  </strong>

                  <span>
                    {document.filename}
                  </span>

                  <span>
                    Uploaded by:{" "}
                    {document.uploaded_by}
                  </span>
                </div>

                <div>
                  <span className="role-badge">
                    {document.document_type}
                  </span>

                  <span className="role-badge">
                    v{document.version}
                  </span>

                  <span className="role-badge">
                    {document.status}
                  </span>

                  <button
                    type="button"
                    className="secondary-button"
                    onClick={() =>
                      handleViewHistory(
                        document.document_name
                      )
                    }
                  >
                    History
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedDocument && (
        <div className="users-list-card">
          <div className="mode-header">
            <div>
              <h3>Version History</h3>

              <p>
                {selectedDocument}
              </p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setSelectedDocument(null);
                setHistory([]);
              }}
            >
              Close
            </button>
          </div>

          {history.length === 0 ? (
            <p>
              No version history found.
            </p>
          ) : (
            <div className="users-list">
              {history.map((version) => (
                <div
                  key={version.document_id}
                  className="user-row"
                >
                  <div>
                    <strong>
                      Version {version.version}
                    </strong>

                    <span>
                      {version.filename}
                    </span>

                    <span>
                      Uploaded by:{" "}
                      {version.uploaded_by}
                    </span>
                  </div>

                  <span className="role-badge">
                    {version.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default KnowledgeBase;