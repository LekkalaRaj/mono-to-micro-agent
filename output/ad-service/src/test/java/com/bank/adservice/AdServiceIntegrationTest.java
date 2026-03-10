package com.bank.adservice;

import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.test.web.servlet.MockMvc;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class AdServiceIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("Health endpoint returns 200 UP")
    void healthEndpoint_returns200() throws Exception {
        mockMvc.perform(get("/api/ads/health"))
               .andExpect(status().isOk())
               .andExpect(content().string("UP"));
    }
}