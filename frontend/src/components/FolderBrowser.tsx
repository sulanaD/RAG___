import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Folder, FolderOpen, FileText } from 'lucide-react';

interface Page {
  chunk_id: string;
  source_path: string;
  page_number: number;
  title: string;
}

interface FolderNode {
  name: string;
  path: string;
  isExpanded: boolean;
  children: FolderNode[];
  pages: Page[];
  isRoot?: boolean;
}

interface FolderBrowserProps {
  pages: Page[];
  selectedPage: number | null;
  onPageSelect: (pageNumber: number) => void;
  pageTitles: Record<string, string>;
}

export function FolderBrowser({ pages, selectedPage, onPageSelect, pageTitles }: FolderBrowserProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null);

  // Build folder tree structure
  const buildFolderTree = (): FolderNode => {
    const root: FolderNode = {
      name: 'Root',
      path: '',
      isExpanded: true,
      children: [],
      pages: [],
      isRoot: true
    };

    const folderMap = new Map<string, FolderNode>();
    folderMap.set('', root);

    // Sort pages by source_path for consistent ordering
    const sortedPages = [...pages].sort((a, b) => a.source_path.localeCompare(b.source_path));

    sortedPages.forEach((page) => {
      const pathParts = page.source_path.split('/').filter(part => part && part !== 'unzipped');
      
      if (pathParts.length === 0) {
        root.pages.push(page);
        return;
      }

      // Create folder nodes for each part of the path
      let currentPath = '';
      let parentNode = root;

      for (let i = 0; i < pathParts.length - 1; i++) {
        const folderName = pathParts[i];
        currentPath = currentPath ? `${currentPath}/${folderName}` : folderName;

        let folderNode = folderMap.get(currentPath);
        if (!folderNode) {
          folderNode = {
            name: folderName,
            path: currentPath,
            isExpanded: false,
            children: [],
            pages: []
          };
          folderMap.set(currentPath, folderNode);
          parentNode.children.push(folderNode);
        }
        parentNode = folderNode;
      }

      // Add page to the appropriate folder or root
      if (pathParts.length === 1) {
        root.pages.push(page);
      } else {
        const folderPath = pathParts.slice(0, -1).join('/');
        const folderNode = folderMap.get(folderPath);
        if (folderNode) {
          folderNode.pages.push(page);
        }
      }
    });

    return root;
  };

  const folderTree = buildFolderTree();

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFolderNode = (node: FolderNode, depth: number = 0): React.ReactNode => {
    const isExpanded = node.isRoot || expandedFolders.has(node.path);
    const hasChildren = node.children.length > 0 || node.pages.length > 0;
    const paddingLeft = depth * 20;

    return (
      <div key={node.path}>
        {/* Folder Header */}
        {!node.isRoot && (
          <div 
            className={`flex items-center py-2 px-3 hover:bg-gray-50 cursor-pointer transition-colors ${
              selectedFolder === node.path ? 'bg-blue-50 border-l-4 border-blue-500' : ''
            }`}
            style={{ paddingLeft: paddingLeft + 12 }}
            onClick={() => {
              if (hasChildren) {
                toggleFolder(node.path);
              }
              setSelectedFolder(node.path);
            }}
          >
            {hasChildren && (
              <>
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 mr-2 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 mr-2 text-gray-400" />
                )}
              </>
            )}
            {!hasChildren && <div className="w-6 mr-2" />}
            
            {isExpanded ? (
              <FolderOpen className="w-4 h-4 mr-2 text-blue-500" />
            ) : (
              <Folder className="w-4 h-4 mr-2 text-gray-500" />
            )}
            
            <span className="text-sm font-medium text-gray-700">{node.name}</span>
            <span className="ml-auto text-xs text-gray-500">
              {node.children.reduce((total, child) => total + child.pages.length, node.pages.length)} items
            </span>
          </div>
        )}

        {/* Folder Contents */}
        {isExpanded && (
          <div>
            {/* Child Folders */}
            {node.children.map(child => renderFolderNode(child, depth + 1))}
            
            {/* Pages in this folder */}
            {node.pages
              .sort((a, b) => {
                // Sort by filename first, then by page number
                const fileA = a.source_path.split('/').pop() || '';
                const fileB = b.source_path.split('/').pop() || '';
                if (fileA !== fileB) return fileA.localeCompare(fileB);
                return a.page_number - b.page_number;
              })
              .map((page) => {
                const fileName = page.source_path.split('/').pop() || '';
                const isSelected = selectedPage === page.page_number;
                
                return (
                  <div
                    key={page.chunk_id}
                    className={`flex items-center py-2 px-3 cursor-pointer transition-colors hover:bg-gray-50 ${
                      isSelected ? 'bg-blue-100 border-l-4 border-blue-500' : ''
                    }`}
                    style={{ paddingLeft: paddingLeft + 32 }}
                    onClick={() => onPageSelect(page.page_number)}
                  >
                    <FileText className="w-4 h-4 mr-2 text-gray-400" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center">
                        <span className="text-sm text-gray-900 font-medium mr-2">
                          {fileName}
                        </span>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          Page {page.page_number}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 mt-1 truncate">
                        {pageTitles[page.chunk_id] || page.title}
                      </div>
                    </div>
                    {isSelected && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full ml-2" />
                    )}
                  </div>
                );
              })}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-3">
        <div className="mb-2 flex items-center justify-between">
          <button
            onClick={() => {
              // Expand all folders
              const allPaths = new Set<string>();
              const collectPaths = (node: FolderNode) => {
                if (!node.isRoot) allPaths.add(node.path);
                node.children.forEach(collectPaths);
              };
              collectPaths(folderTree);
              setExpandedFolders(allPaths);
            }}
            className="text-xs text-blue-600 hover:text-blue-800"
          >
            Expand All
          </button>
        </div>
        
        <div className="border border-gray-200 rounded-lg overflow-hidden bg-white">
          {renderFolderNode(folderTree)}
        </div>
        
        {/* Compact Summary Stats */}
        <div className="mt-3 p-2 bg-gray-50 rounded text-xs text-gray-600">
          <div className="flex justify-between">
            <span>Pages: {pages.length}</span>
            <span>Folders: {folderTree.children.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
}