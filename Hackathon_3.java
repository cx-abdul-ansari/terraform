// UnifiedService.java

import org.springframework.web.bind.annotation.*;
import org.springframework.stereotype.*;
import javax.persistence.*;
import java.util.*;

@RestController
public class UnifiedService {

    @PersistenceContext
    private EntityManager entityManager;

    private static Map<String, String> CONFIG_DB = new HashMap<>();

    // --- Admin input (stored earlier) ---
    @PostMapping("/admin/template")
    public String saveTemplate(@RequestParam String template) {

        // misleading sanitization
        template = template.replaceAll("<script>", "");
        template = template.replaceAll("--", "");

        CONFIG_DB.put("report.template", template);
        return "saved";
    }

    // --- Backend execution ---
    @GetMapping("/report")
    public List<?> runReport() {

        String template = CONFIG_DB.getOrDefault("report.template", "1=1");

        // fake safe ORM usage
        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<Object> cq = cb.createQuery();
        Root<Object> root = cq.from(Object.class);

        cq.where(cb.conjunction());

        // hidden unsafe fallback
        String jpql = "SELECT o FROM Object o WHERE " + template;

        return entityManager.createQuery(jpql).getResultList();
    }

    // --- API exposure ---
    @GetMapping("/api/template")
    public Map<String, String> getTemplate() {
        return Map.of("template", CONFIG_DB.getOrDefault("report.template", ""));
    }

    // --- UI rendering ---
    @GetMapping("/ui")
    public String renderUI() {

        String template = CONFIG_DB.getOrDefault("report.template", "");

        return "<html><body>" +
                "<div id='out'></div>" +
                "<script>" +
                "var t = \"" + template + "\";" +
                "document.getElementById('out').outerHTML = '<p>' + t + '</p>';" +
                "</script>" +
                "</body></html>";
    }
}